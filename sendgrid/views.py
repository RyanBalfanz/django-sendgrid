from __future__ import absolute_import

import json
import logging
from datetime import datetime
from django.conf import settings
from django.db import transaction, models
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from .signals import sendgrid_event_recieved

from sendgrid.constants import BATCHED_EVENT_SEPARATOR, EVENT_TYPES_EXTRA_FIELDS_MAP, EVENT_MODEL_NAMES, NEWSLETTER_UNIQUE_IDENTIFIER, UNIQUE_ARGS_STORED_FOR_NEWSLETTER_EVENTS
from sendgrid.models import EmailMessage, Event, ClickEvent, DeferredEvent, DroppedEvent, DeliverredEvent, BounceEvent, EventType, Category, Argument, UniqueArgument
from sendgrid.utils.formatutils import convert_flat_dict_to_nested
from sendgrid.utils.formatutils import get_value_from_dict_using_formdata_key
from sendgrid.utils.dbutils import flush_transaction
from sendgrid import settings as sendgrid_settings

POST_EVENTS_RESPONSE_STATUS_CODE = getattr(settings, "POST_EVENT_HANDLER_RESPONSE_STATUS_CODE", 200)

logger = logging.getLogger(__name__)

def find_email(message_id,emails):
	for email in emails:
		if email.message_id == message_id:
			return email

	return None

def find_newsletter_email(to_email,emails):
	for email in emails:
		if email.to_email == to_email:
			return email

	return None

def build_email_from_newsletter_event(newsletter_event):
	categories = newsletter_event.get("category",[])
	if type(categories) == basestring:
		categories = [categories]

	newsletterId = get_value_from_dict_using_formdata_key(NEWSLETTER_UNIQUE_IDENTIFIER,newsletter_event)
	email = EmailMessage(
		from_email=newsletterId,
		to_email=newsletter_event.get("email",None),
		response=None,
		category=categories[0]
	)
	return email

def build_event(event,email_message):
	eventType = EventType.objects.get(name=event["event"].upper())
	eventParams = {
		"email_message": email_message,
		"email": event["email"],
		"event_type": eventType
	}
	timestamp = event.get("timestamp", None)
	if timestamp:
		eventParams["timestamp"] = datetime.utcfromtimestamp(float(timestamp))

		#enforce unique constraint on email_message,event_type,creation_time
		#this should be done at the db level but since it was added later it would have needed a data migration that either deleted or updated duplicate events
		#this also might need a combined index, but django orm doesn't have this feature yet: https://code.djangoproject.com/ticket/5805
		existingEvents = Event.objects.filter(email_message=email_message,event_type=eventType,timestamp=eventParams["timestamp"])
		unique = existingEvents.count() == 0
	else:
		#no timestamp provided. therefore we cannot enforce any kind of uniqueness
		unique = True

	eventObj = None
	if unique:
		for key in EVENT_TYPES_EXTRA_FIELDS_MAP[eventType.name]:
			value = event.get(key,None)
			if value:
				eventParams[key] = value
			else:
				logger.debug("Expected post param {key} for Sendgrid Event {event} not found".format(key=key,event=event))
		event_model = eval(EVENT_MODEL_NAMES[event]) if event in EVENT_MODEL_NAMES.keys() else Event

	return event_model(**eventParams)

def seperate_events_by_newsletter_id(events):
	eventsByNewsletter = {}
	for event in events:
		newsletterId = get_value_from_dict_using_formdata_key(NEWSLETTER_UNIQUE_IDENTIFIER,event)
		if newsletterId:
			if eventsByNewsletter.get(newsletterId,None) != None:
				eventsByNewsletter[newsletterId].append(event)
			else:
				eventsByNewsletter[newsletterId] = [event]

	return eventsByNewsletter

@transaction.commit_on_success
def bulk_create_emails_with_manual_ids(emails):
    start = (EmailMessage.objects.all().aggregate(models.Max('id'))['id__max'] or 0) + 1
    for i,email in enumerate(emails): 
    	email.id = start + i
    return EmailMessage.objects.bulk_create(emails)


def batch_create_newsletter_events(newsletter_id,events):
	flush_transaction()
	toEmails = [event.get("email",None) for event in events]
	existingNewsletterEmails = EmailMessage.objects.filter(
		uniqueargument__data=newsletter_id, 
		uniqueargument__argument__key=NEWSLETTER_UNIQUE_IDENTIFIER, 
		to_email__in=toEmails
	)

	newsletterEmailsToCreate = []
	newsletterEventTuplesWithoutEmails = []
	newsletterEventsWithEmails = []
	for newsletterEvent in events:
		toEmail = newsletterEvent.get("email",None)
		existingNewsletterEmail = find_newsletter_email(toEmail,existingNewsletterEmails)

		if not existingNewsletterEmail:
			emailToCreate = build_email_from_newsletter_event(newsletterEvent)
			newsletterEmailsToCreate.append(emailToCreate)

			eventToCreate = build_event(newsletterEvent,emailToCreate)
			newsletterEventTuplesWithoutEmails.append((eventToCreate,event))
		else:
			#create the event and attach it to the email
			eventToCreate = build_event(newsletterEvent,existingNewsletterEmail)
			newsletterEventsWithEmails.append(eventToCreate)

	Event.objects.bulk_create(newsletterEventsWithEmails)
	
	flush_transaction()		
	newEmails = bulk_create_emails_with_manual_ids(newsletterEmailsToCreate)

	uniqueArgsToCreate = []
	categoriesToCreate = []

	for event,eventDict in newsletterEventTuplesWithoutEmails:
		email = [email for email in newEmails if email.to_email == event.email][0]
		categories = eventDict["category"]
		if type(categories) == basestring:
			categories = [categories]
		event.email_message = email
		for category in categories:
			categoryObj,_ = Category.objects.get_or_create(name=category)
			categoriesToCreate.append(email.categories.through(category=categoryObj, emailmessage=email))

		uniqueArgs = {}
		for key in UNIQUE_ARGS_STORED_FOR_NEWSLETTER_EVENTS:
			uniqueArgs[key] = get_value_from_dict_using_formdata_key(key,eventDict)

		for argName, argValue in uniqueArgs.items():
			flush_transaction()
			argument,_ = Argument.objects.get_or_create(
				key=argName
			)
			uniqueArgsToCreate .append(UniqueArgument(
				argument=argument,
				email_message=email,
				data=argValue
			))

	EmailMessage.categories.through.objects.bulk_create(categoriesToCreate)
	UniqueArgument.objects.bulk_create(uniqueArgsToCreate)
	Event.objects.bulk_create([tup[0] for tup in newsletterEventTuplesWithoutEmails])

	

	#createdEmails = 
	#for toEmail in newsletterEmailsToCreate:

	#categories

def batch_create_events(events):
	#split events into 2 groups
	#first group is events with message_ids
	eventsWithMessageIds = [event for event in events if event.get("message_id",None)]

	#check for newsletter events
	if sendgrid_settings.SENDGRID_CREATE_EVENTS_AND_EMAILS_FOR_NEWSLETTERS:
		

		newsletterEvents = [event for event in events if (not event.get("message_id",None)) and event.get("newsletter",None)]

		newsletterEventsByNewsletter = seperate_events_by_newsletter_id(newsletterEvents)
		for newsletterId, events in newsletterEventsByNewsletter.items():
			batch_create_newsletter_events(newsletterId,events)
		



	
	messageIds = [event.get("message_id",None) for event in eventsWithMessageIds if event.get("message_id",None)]
	flush_transaction()
	#batch select email messages from db
	existingEmailMessages = EmailMessage.objects.filter(message_id__in=messageIds)

	for event in eventsWithMessageIds:
		existingEmailMessage = [emailMessage for emailMessage in existingEmailMessages if emailMessage.message_id == event.get("message_id",None)]
		
	eventsWithMessageIds = [{"event":event} for event in events if event.get("message_id",None)]


	#second group is message_id given and email doesn't exist

	#third group is newsletter events

def create_event_from_sendgrid_params(params,create=True):
	flush_transaction()
	email = params.get("email", None)
	event = params.get("event", None).upper()
	category = params.get("category", None)
	if type(category) == str:
		category = [category]

	message_id = params.get("message_id", None)

	emailMessage = None
	if message_id:
		try:
			flush_transaction()
			emailMessage = EmailMessage.objects.get(message_id=message_id)
		except EmailMessage.DoesNotExist:
			msg = "EmailMessage with message_id {id} not found"
			logger.debug(msg.format(id=message_id))
	else:
		msg = "Expected 'message_id' was not found in event data"
		logger.debug(msg)

	if not emailMessage:
		if sendgrid_settings.SENDGRID_CREATE_MISSING_EMAILS_FOR_EVENTS_WITH_MESSAGE_ID and message_id:
			emailMessage = EmailMessage.from_event(params)
		elif sendgrid_settings.SENDGRID_CREATE_EVENTS_AND_EMAILS_FOR_NEWSLETTERS and params.get("newsletter",None):
			emailMessage = EmailMessage.from_event(params)

	if not emailMessage:
		logger.debug("Couldn't create email message for event with params {0}".format(params))
		return None

	event_type = EventType.objects.get(name=event.upper())
	event_params = {
		"email_message": emailMessage,
		"email": email,
		"event_type": event_type
	}
	timestamp = params.get("timestamp", None)
	if timestamp:
		event_params["timestamp"] = datetime.utcfromtimestamp(float(timestamp))

		#enforce unique constraint on email_message,event_type,creation_time
		#this should be done at the db level but since it was added later it would have needed a data migration that either deleted or updated duplicate events
		#this also might need a combined index, but django orm doesn't have this feature yet: https://code.djangoproject.com/ticket/5805
		existingEvents = Event.objects.filter(email_message=emailMessage,event_type=event_type,timestamp=event_params["timestamp"])
		unique = existingEvents.count() == 0
	else:
		#no timestamp provided. therefore we cannot enforce any kind of uniqueness
		unique = True
	if unique:
		for key in EVENT_TYPES_EXTRA_FIELDS_MAP[event.upper()]:
			value = params.get(key,None)
			if value:
				event_params[key] = value
			else:
				logger.debug("Expected post param {key} for Sendgrid Event {event} not found".format(key=key,event=event))
		event_model = eval(EVENT_MODEL_NAMES[event]) if event in EVENT_MODEL_NAMES.keys() else Event
		if create:
			eventObj = event_model.objects.create(**event_params)
		else:
			eventObj = event_model(**event_params)

	return eventObj

def handle_single_event_request(request):
	"""
	Handles single event POST requests.
	"""
	eventData = request.POST
	eventData = convert_flat_dict_to_nested(eventData)
	create_event_from_sendgrid_params(eventData)
	
	response = HttpResponse()

	return response

def handle_batched_events_request(request):
	"""
	Handles batched events POST requests.

	Example batched events ::

		{"email":"foo@bar.com","timestamp":1322000095,"unique_arg":"my unique arg","event":"delivered"}
		{"email":"foo@bar.com","timestamp":1322000096,"unique_arg":"my unique arg","event":"open"}

	Note: Not using bulk inserts for now because post_save/pre_save would not be triggered.
	"""
	# https://docs.djangoproject.com/en/dev/releases/1.4/#httprequest-raw-post-data-renamed-to-httprequest-body
	try:
		body = request.body
	except AttributeError:
		import warnings
		warnMsg = "django-sendgrid will require at least Django 1.4 in future releases"
		warnings.warn(warnMsg, FutureWarning)

		body = request.raw_post_data

	events = [json.loads(line) for line in body.splitlines()]
	eventsToSave = []
	for event in events:
		eventToSave = create_event_from_sendgrid_params(event,False)
		if eventToSave:
			eventsToSave.append(eventToSave)

	Event.objects.bulk_create(eventsToSave)
		
	return HttpResponse()

def clean_response(response):
	expectedStatusCode = POST_EVENTS_RESPONSE_STATUS_CODE

	if not response:
		logger.error("A response was not created!")
		response = HttpResponse()

	if response.status_code != expectedStatusCode:
		logger.debug("Attempted to send status code {c}".format(c=response.status_code))
		logger.debug("Setting status code to {c}".format(c=expectedStatusCode))

		response.write("Previous status code: {c}\n".format(c=response.status_code))
		response.status_code = expectedStatusCode

	return response

@csrf_exempt
def listener(request, statusCode=POST_EVENTS_RESPONSE_STATUS_CODE):
	"""
	Handles POSTs from SendGrid

	# SendGrid Event API Documentation
	# http://docs.sendgrid.com/documentation/api/event-api/
	
	Example Request ::
		
		curl -i -d 'message_id=1&amp;email=test@gmail.com&amp;arg2=2&amp;arg1=1&amp;category=testing&amp;event=processed' http://127.0.0.1:8000/sendgrid/events/
	"""
	sendgrid_event_recieved.send(sender=None, request=request)

	response = None
	if request.method == "POST":
		if request.META["CONTENT_TYPE"].startswith("application/json"):
			# Batched event POSTs have a content-type header of application/json
			# They contain exactly one JSON string per line, with each line representing one event.
			response = handle_batched_events_request(request)
		elif request.META["CONTENT_TYPE"].startswith("application/xml"):
			raise NotImplementedError
		elif request.META["CONTENT_TYPE"].startswith("application/x-www-form-urlencoded"):
			response = handle_single_event_request(request)
		else:
			msg = "Unexpected content type: {m}".format(m=request.META["CONTENT_TYPE"])
			logger.error(msg)
	else:
		msg = "Request method '{method}' not allowed: {error}".format(method=request.method, error=request.method)
		logger.error(msg)
		
		response = HttpResponse()
		response.status_code = 405

	return clean_response(response)

def download_attachments(request, message_id):
	"""
	Returns an HttpResponse containing the zipped attachments.
	"""
	import zipfile
	from contextlib import closing
	from django.shortcuts import get_object_or_404
	from django.utils import simplejson as json

	from sendgrid.utils import zip_files

	emailMessage = get_object_or_404(EmailMessage, message_id=message_id)

	emailMessageDataString = emailMessage.attachments_data
	if emailMessageDataString:
		# TODO: This is a little hacky
		emailMessageDataStringJSONSafe = (emailMessageDataString
			.replace('(', '[')
			.replace(')', ']')
			.replace("'", '"')
			.replace("None", '"text/plain"')
		)
		obj = json.loads(emailMessageDataStringJSONSafe)

		files = {}
		for name, content, contentType in obj:
			files[name] = content

		response = HttpResponse(mimetype="application/x-zip")
		response["Content-Disposition"] = "attachment; filename={filename}".format(filename="attachment.zip")
		with closing(zip_files(files)) as zio:
			response.write(zio.getvalue())
	else:
		response = HttpResponseNotFound()
		response.write("The attachments were not found")

	return response

