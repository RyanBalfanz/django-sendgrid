from __future__ import absolute_import

import logging

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from .signals import sendgrid_event_recieved

from sendgrid.models import EmailMessage, Event, EventType


POST_EVENTS_RESPONSE_STATUS_CODE = getattr(settings, "POST_EVENT_HANDLER_RESPONSE_STATUS_CODE", 200)

logger = logging.getLogger(__name__)

def handle_single_event_request(request):
	"""
	Handles single event POST requests.
	"""
	eventData = request.POST

	# Parameters that are always passed with each event
	email = eventData.get("email", None)
	event = eventData.get("event", None)

	message_id = eventData.get("message_id", None)
	if message_id:
		try:
			emailMessage = EmailMessage.objects.get(message_id=message_id)
		except EmailMessage.DoesNotExist:
			msg = "EmailMessage with message_id {m} does not exist"
			logger.exception(msg.format(m=message_id))

			response = HttpResponseNotFound()
			response.write(msg.format(m=message_id) + "\n")
		else:
			eventObj = Event.objects.create(
				email_message=emailMessage,
				email=email,
				type=EventType.objects.get(name=event.upper()),
			)

			response = HttpResponse()
	else:
		msg = "Expected 'message_id' was not found in event data"
		logger.exception(msg)

		response = HttpResponseBadRequest()
		response.write(msg + "\n")

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
