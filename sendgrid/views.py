from __future__ import absolute_import

import logging

from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from .signals import sendgrid_event_recieved


logger = logging.getLogger(__name__)

def process_event_data(eventData):
	"""docstring for process_event"""
	raise NotImplementedError

def handle_single_event_request(request):
	"""
	Handles single event POST requests.
	"""
	email = request.POST.get("email", None)
	event = request.POST.get("event", None)
	if not email or not event:
		response = HttpResponseBadRequest()
	else:
		sendgrid_event_recieved.send(sender=None, email=email, event=event)
		
		response = HttpResponse()
		
		logger.debug("\n".join(map(str, [email, event])) + "\n")
		
	return response

def handle_batched_events_request(request):
	"""
	Handles batched events POST requests.
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
	
	print "REQUEST METHOD:", request.method
	
	response = None
	if request.method == 'POST':
		print "POST:", request.POST
		
		if request.META["CONTENT_TYPE"] == "application/json":
			response = handle_batched_events_request(request)
		elif request.META["CONTENT_TYPE"] == "application/xml":
			response = handle_single_event_request(request)
		elif request.META["CONTENT_TYPE"] == "application/x-www-form-urlencoded":
			response = handle_single_event_request(request)
		else:
			msg = "MIME type {m} unexpected".format(m=request.META["CONTENT_TYPE"])
			logger.error(msg)
			# raise Exception(msg)
	else:
		msg = "Request method not allowed: {error}".format(error=request.method)
		logger.error(msg)
		
		# Method Not Allowed
		response = HttpResponse()
		response.status_code = 405
		
	if not response:
		logger.error("A response was not created!")
		response = HttpResponse()
		
	return response
