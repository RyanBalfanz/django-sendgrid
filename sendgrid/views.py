from __future__ import absolute_import

import logging

from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from .signals import sendgrid_event_recieved


REQUIRED_KEYS = ("email", "event")
OPTIONAL_KEYS = ("category")

logger = logging.getLogger(__name__)


class SendGridEventValueError(ValueError):
	pass


def handle_single_json_event(e):
	"""
	Handles a single JSON event -- i.e. a single line in batched events.

	Example JSON event ::

		{"email":"foo@bar.com","timestamp":1322000095,"unique_arg":"my unique arg","event":"delivered"}

	"""
	if isinstance(e, basestring):
		e = simplejson.loads(e)

	email = e.get("email", None)
	event = e.get("event", None)
	category = e.get("category", None)
	keyIsUniqueArg = lambda k: k not in REQUIRED_KEYS and k not in OPTIONAL_KEYS
	uniqueArgs = dict(((k, v) for (k, v) in e.iteritems() if keyIsUniqueArg(k)))

	if not email or not event:
		raise SendGridEventValueError

	return True

def convert_single_event_request_to_json_event(request):
	"""
	Returns a JSON-style event.
	"""
	postData = request.POST
	logger.debug("Post data: {0}".format(postData))

	# Parameters that are always passed with each event
	email = postData.get("email", None)
	event = postData.get("event", None)
	
	# Optional parameters and categories
	category = postData.get("category", None)
	
	# Custon parameters, unique arguments
	uniqueArgs = {}
	for k, v in postData.iteritems():
		if k in REQUIRED_KEYS or k in OPTIONAL_KEYS:
			continue
		else:
			uniqueArgs[k] = v

	logger.debug("Unique Args: {0}".format(uniqueArgs))

	eventDict = {
		"email": email,
		"event": event,
	}
	eventDict.update(uniqueArgs)
	jsonEvent = simplejson.dumps(eventDict)

	return jsonEvent

def handle_single_event_request(request):
	"""
	Handles single event POST requests.
	"""
	jsonEvent = convert_single_event_request_to_json_event(request)
	jsonEvent = simplejson.loads(jsonEvent)

	try:
		handle_single_json_event(jsonEvent)
	except SendGridEventValueError:
		response = HttpResponseBadRequest()
	else:
		# sendgrid_event_recieved.send(sender=None, email=email, event=event)
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

@csrf_exempt
def listener(request):
	"""
	Handles POSTs from SendGrid

	# SendGrid Event API Documentation
	# http://docs.sendgrid.com/documentation/api/event-api/
	
	Example Request ::
		
		curl -i -d 'email=test@gmail.com&amp;arg2=2&amp;arg1=1&amp;category=testing&amp;event=processed' http://127.0.0.1:8000/sendgrid/events/
	"""
	sendgrid_event_recieved.send(sender=None)
		
	response = None
	if request.method == 'POST':
		if request.META["CONTENT_TYPE"] == "application/json":
			# Batched event POSTs have a content-type header of application/json
			# They contain exactly one JSON string per line, with each line representing one event.
			response = handle_batched_events_request(request)
		elif request.META["CONTENT_TYPE"] == "application/xml":
			response = handle_single_event_request(request)
		elif request.META["CONTENT_TYPE"] == "application/x-www-form-urlencoded":
			response = handle_single_event_request(request)
		else:
			msg = "Unexpected content type: {m}".format(m=request.META["CONTENT_TYPE"])
			logger.error(msg)
	else:
		msg = "Request method not allowed: {error}".format(error=request.method)
		logger.error(msg)
		
		response = HttpResponse()
		response.status_code = 405
		
	if not response:
		logger.error("A response was not created!")
		response = HttpResponse()
		
	return response
