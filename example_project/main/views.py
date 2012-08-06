from __future__ import absolute_import

import logging

from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# django-sendgrid
from sendgrid.mail import send_sendgrid_mail
from sendgrid.message import SendGridEmailMessage
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
			subject = request.POST["subject"]
			message = request.POST["message"]
			from_email = request.POST["sender"]
			recipient_list = request.POST["to"]
			recipient_list = [r.strip() for r in recipient_list.split(",")]
			categoryData = request.POST["category"]
			categories = parse_csv_string(categoryData)
			# https://docs.djangoproject.com/en/dev/ref/forms/fields/#booleanfield
			html = getattr(request.POST, "html", False)
			enable_gravatar = getattr(request.POST, "enable_gravatar", False)
			enable_click_tracking = getattr(request.POST, "enable_click_tracking", False)
			add_unsubscribe_link = getattr(request.POST, "add_unsubscribe_link", False)

			sendGridEmail = SendGridEmailMessage(
				subject,
				message,
				from_email,
				recipient_list,
			)
			if html:
				sendGridEmail.content_subtype = "html"
				
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
			return HttpResponseRedirect("/")
	else:
		form = EmailForm()

	c = { "form": form }
	c.update(csrf(request))
	return render_to_response('main/send_email.html', c)
