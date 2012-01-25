import logging
import json

from django.conf import settings
from django.core import mail
from django.core.mail.message import EmailMessage

# django-sendgrid imports
from header import SmtpApiHeader
from mail import get_sendgrid_connection
from signals import sendgrid_email_sent


logger = logging.getLogger(__name__)


class SendGridEmailMessage(EmailMessage):
	"""
	Adapts Django's ``EmailMessage`` for use with SendGrid.
	
	>>> from sendgrid.message import SendGridEmailMessage
	>>> myEmail = "rbalfanz@gmail.com"
	>>> mySendGridCategory = "django-sendgrid"
	>>> e = SendGridEmailMessage("Subject", "Message", myEmail, [myEmail], headers={"Reply-To": myEmail})
	>>> e.sendgrid_headers.setCategory(mySendGridCategory)
	>>> e.update_headers()
	>>> response = e.send()
	"""
	sendgrid_headers = SmtpApiHeader()
	
	def __init__(self, *args, **kwargs):
		"""
		Initialize the object.
		"""
		super(SendGridEmailMessage, self).__init__(*args, **kwargs)
		
	def _update_headers_with_sendgrid_headers(self):
		"""
		Updates the existing headers to include SendGrid headers.
		"""
		logger.debug("Updating headers with SendGrid headers")
		sendgrid_headers_dict = dict(json.loads(self.sendgrid_headers.asJSON()))
		self.extra_headers.update(sendgrid_headers_dict)
		logging.debug(str(self.extra_headers))
		
		return self.extra_headers
		
	def update_headers(self, *args, **kwargs):
		"""
		Updates the headers.
		"""
		return self._update_headers_with_sendgrid_headers(*args, **kwargs)
		
	def send(self, *args, **kwargs):
		"""Sends the email message."""
		# Set up the connection
		connection = get_sendgrid_connection()
		self.connection = connection
		logger.debug("Connection: {c}".format(c=connection))
		
		self.sendgrid_headers.setCategory("django-sendgrid-test")
		self.update_headers()
		
		response = super(SendGridEmailMessage, self).send(*args, **kwargs)
		logger.debug("Tried to send an email with SendGrid and got response {r}".format(r=response))
		sendgrid_email_sent.send(sender=self, response=response)
		
		return response
