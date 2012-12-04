from __future__ import absolute_import

import logging

from django.contrib import messages
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# django-sendgrid
from sendgrid.mail import send_sendgrid_mail
from sendgrid.message import SendGridEmailMessage
from sendgrid.message import SendGridEmailMultiAlternatives
from sendgrid.utils import filterutils

# example_project
from .forms import EmailForm

DEFAULT_CSV_SEPARATOR = ","

logger = logging.getLogger(__name__)

def parse_csv_string(s, separator=DEFAULT_CSV_SEPARATOR):
	return [field.strip() for field in s.split(separator) if field]

def send_simple_email(request):
	if request.method == 'POST':
		form = EmailForm(request.POST)
		if form.is_valid():
			subject = form.cleaned_data["subject"]
			message = form.cleaned_data["message"]
			from_email = form.cleaned_data["sender"]
			recipient_list = form.cleaned_data["to"]
			recipient_list = [r.strip() for r in recipient_list.split(",")]
			categoryData = form.cleaned_data["categories"]
			categories = parse_csv_string(categoryData)
			html = form.cleaned_data["html"]
			enable_gravatar = form.cleaned_data["enable_gravatar"]
			enable_click_tracking = form.cleaned_data["enable_click_tracking"]
			add_unsubscribe_link = form.cleaned_data["add_unsubscribe_link"]

			if html:
				sendGridEmail = SendGridEmailMultiAlternatives(
					subject,
					message,
					from_email,
					recipient_list,
				)
				sendGridEmail.attach_alternative(message, "text/html")
			else:
				sendGridEmail = SendGridEmailMessage(
					subject,
					message,
					from_email,
					recipient_list,
				)
				
			if categories:
				logger.debug("Categories {c} were given".format(c=categories))
				# The SendGrid Event API will POST different data for single/multiple category messages.
				if len(categories) == 1:
					sendGridEmail.sendgrid_headers.setCategory(categories[0])
				elif len(categories) > 1:
					sendGridEmail.sendgrid_headers.setCategory(categories)
				sendGridEmail.update_headers()
				
			filterSpec = {}
			if enable_gravatar:
				logger.debug("Enable Gravatar was selected")
				filterSpec["gravatar"] = {
					"enable": 1
				}
				
			if enable_gravatar:
				logger.debug("Enable click tracking was selected")
				filterSpec["clicktrack"] = {
					"enable": 1
				}
				
			if add_unsubscribe_link:
				logger.debug("Add unsubscribe link was selected")
				# sendGridEmail.sendgrid_headers.add
				filterSpec["subscriptiontrack"] = {
					"enable": 1,
					"text/html": "<p>Unsubscribe <%Here%></p>",
				}
				
			if filterSpec:
				filterutils.update_filters(sendGridEmail, filterSpec, validate=True)
				
			logger.debug("Sending SendGrid email {e}".format(e=sendGridEmail))
			response = sendGridEmail.send()
			logger.debug("Response {r}".format(r=response))

			if response == 1:
				msg = "Your message was sent"
				msgType = messages.SUCCESS
			else:
				msg = "The was en error sending your message"
				msgType = messages.ERROR
			messages.add_message(request, msgType, msg)

			return HttpResponseRedirect("/")
	else:
		form = EmailForm()

	c = { "form": form }
	c.update(csrf(request))
	return render_to_response('main/send_email.html', c)
