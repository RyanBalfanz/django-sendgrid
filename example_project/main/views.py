from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from main.forms import EmailForm
from sendgrid.utils import send_email_with_sendgrid
from sendgrid.message import SendGridEmailMessage

def send_simple_email(request):
	if request.method == 'POST': # If the form has been submitted...
		form = EmailForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			subject=request.POST["subject"]
			message=request.POST["message"]
			from_email=request.POST["sender"]
			recipient_list=[request.POST["to"]]
			
			# send_email_with_sendgrid(
			# 	subject=request.POST["subject"],
			# 	message=request.POST["message"],
			# 	from_email=request.POST["sender"],
			# 	recipient_list=[request.POST["to"]])
				
			email = SendGridEmailMessage(
				subject,
				message,
				from_email,
				['ryan@mindsnacks.com'],
			)
			email.send()
			return HttpResponseRedirect('/') # Redirect after POST
	else:
		form = EmailForm() # An unbound form

	c = { "form": form }
	c.update(csrf(request))
	return render_to_response('main/send_email.html', c)
