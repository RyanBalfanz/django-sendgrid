from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from main.forms import EmailForm
from sendgrid.utils import send_email_with_sendgrid
from sendgrid.message import SendGridEmailMessage

from signals import sendgrid_event_recieved

def sendgrid_event_recieved_view(request):
	"""
	Handles POSTs to 
	"""
	
	sendgrid_event_recieved.send(request=request)
	

	return render_to_response('main/send_email.html', c)
