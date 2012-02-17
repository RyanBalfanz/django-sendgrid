import logging

from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# example_project
from main.forms import EmailForm

# django-sendgrid
from sendgrid.mail import send_sendgrid_mail
from sendgrid.message import SendGridEmailMessage
from sendgrid.utils import filterutils


logger = logging.getLogger(__name__)


def send_simple_email(request):
	if request.method == 'POST':
		form = EmailForm(request.POST)
		if form.is_valid():
			subject = request.POST["subject"]
			message = request.POST["message"]
			from_email = request.POST["sender"]
			recipient_list = request.POST["to"]
			recipient_list = [r.strip() for r in recipient_list.split(",")]
			category = request.POST["category"]
			html = request.POST["html"]
			add_unsubscribe_link = request.POST["add_unsubscribe_link"]
			
			sendGridEmail = SendGridEmailMessage(
				subject,
				message,
				from_email,
				recipient_list,
			)
			if html:
				sendGridEmail.content_subtype = "html"
				
			if category:
				logger.debug("Category {c} was given".format(c=category))
				sendGridEmail.sendgrid_headers.setCategory(category)
				sendGridEmail.update_headers()
				
			if add_unsubscribe_link:
				logger.debug("Add unsubscribe link was selected")
				# sendGridEmail.sendgrid_headers.add
				filterSpec = {
					"subscriptiontrack": {
						"enable": "1",
						"text/html": "<p>Unsubscribe <%Here%></p>",
					}
				}
				filterutils.update_filters(sendGridEmail, filterSpec, validate=False)
				
			logger.debug("Sending SendGrid email {e}".format(e=sendGridEmail))
			response = sendGridEmail.send()
			logger.debug("Response {r}".format(r=response))
			return HttpResponseRedirect('/')
	else:
		form = EmailForm()

	c = { "form": form }
	c.update(csrf(request))
	return render_to_response('main/send_email.html', c)
