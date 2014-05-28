from __future__ import absolute_import

import logging
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from .signals import sendgrid_event_recieved

from sendgrid.models import EmailMessage, Event, ClickEvent, DeferredEvent, DroppedEvent, DeliverredEvent, BounceEvent, EventType
from sendgrid.constants import EVENT_TYPES_EXTRA_FIELDS_MAP, EVENT_MODEL_NAMES
from sendgrid.settings import SENDGRID_CREATE_MISSING_EMAIL_MESSAGES


POST_EVENTS_RESPONSE_STATUS_CODE = getattr(settings, "POST_EVENT_HANDLER_RESPONSE_STATUS_CODE", 200)

logger = logging.getLogger(__name__)

def handle_single_event_request(request):
	"""
	Handles single event POST requests.
	"""
	eventData = request.POST

	# Parameters that are always passed with each event
	email = eventData.get("email", None)
	event = eventData.get("event", None).upper()
	category = eventData.get("category", None)
	message_id = eventData.get("message_id", None)

	emailMessage = None
	if message_id:
		try:
			emailMessage = EmailMessage.objects.get(message_id=message_id)
		except EmailMessage.DoesNotExist:
			msg = "EmailMessage with message_id {id} not found"
			logger.debug(msg.format(id=message_id))
	else:
		msg = "Expected 'message_id' was not found in event data"
		logger.debug(msg)

	if not emailMessage and SENDGRID_CREATE_MISSING_EMAIL_MESSAGES:
		logger.debug("Creating missing EmailMessage from event data")
		emailMessage = EmailMessage.from_event(eventData)
	elif not emailMessage and not SENDGRID_CREATE_MISSING_EMAIL_MESSAGES:
		return HttpResponse()

	event_type = EventType.objects.get(name=event.upper())
	event_params = {
		"email_message": emailMessage,
		"email": email,
		"event_type":event_type
	}
	timestamp = eventData.get("timestamp",None)
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
			value = eventData.get(key,None)
			if value:
				event_params[key] = value
			else:
				logger.debug("Expected post param {key} for Sendgrid Event {event} not found".format(key=key,event=event))
		event_model = eval(EVENT_MODEL_NAMES[event]) if event in EVENT_MODEL_NAMES.keys() else Event
		eventObj = event_model.objects.create(**event_params)

	response = HttpResponse()

	return response

def handle_batched_events_request(request):
	"""
	Handles batched events POST requests.

	Example batched events ::

		{"email":"foo@bar.com","timestamp":1322000095,"unique_arg":"my unique arg","event":"delivered"}
		{"email":"foo@bar.com","timestamp":1322000096,"unique_arg":"my unique arg","event":"open"}

	"""
	logger.exception("Batched events are not currently supported!")
	raise NotImplementedError

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
	try:
		import json
	except ImportError:
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

