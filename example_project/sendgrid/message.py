import logging

from django.core import mail
from django.core.mail.message import EmailMessage

# django-sendgrid imports
from signals import sendgrid_email_sent

logger = logging.getLogger(__name__)


class SendGridEmailMessage(EmailMessage):
	"""
	Adapts Django's ``EmailMessage`` for use with SendGrid.
	"""
	sendgrid_headers = None
	
	def __init__(self, *args, **kwargs):
		super(SendGridEmailMessage, self).__init__(*args, **kwargs)
		
	def _get_sendgrid_connection(self):
		"""docstring for _get_sendgrid_connection"""
		logger.debug("Getting SendGrid connection")
		connection = mail.get_connection("sendgrid.backends.SendGridEmailBackend")
		return connection
		
	def send(self, *args, **kwargs):
		"""Sends the email message."""
		connection = self._get_sendgrid_connection()
		logger.debug("Connection: {c}".format(c=connection))
		
		response = super(SendGridEmailMessage, self).send(*args, **kwargs)
		sendgrid_email_sent.send(sender=self, email=self.message, response=response)
		
		return response
		