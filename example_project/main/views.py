from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from main.forms import EmailForm
from sendgrid.utils import send_email_with_sendgrid
from sendgrid.message import SendGridEmailMessage

def send_simple_email(request):
	if request.method == 'POST':
		form = EmailForm(request.POST)
		if form.is_valid():
			subject=request.POST["subject"]
			message=request.POST["message"]
			from_email=request.POST["sender"]
			recipient_list=request.POST["to"]
			recipient_list = [r.strip() for r in recipient_list.split(",")]
			
			sendGridEmail = SendGridEmailMessage(
				subject,
				message,
				from_email,
				recipient_list,
			)
			sendGridEmail.send()
			return HttpResponseRedirect('/')
	else:
		form = EmailForm()

	c = { "form": form }
	c.update(csrf(request))
	return render_to_response('main/send_email.html', c)
