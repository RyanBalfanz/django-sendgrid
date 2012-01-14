import logging

from django.conf import settings
from django.core import mail
from django.core.mail.message import EmailMessage

# django-sendgrid imports
from signals import sendgrid_email_sent

logger = logging.getLogger(__name__)

SENDGRID_EMAIL_BACKEND = getattr(settings, "SENDGRID_EMAIL_BACKEND", "sendgrid.backends.SendGridEmailBackend")


class SendGridEmailMessage(EmailMessage):
	"""
	Adapts Django's ``EmailMessage`` for use with SendGrid.
	"""
	sendgrid_headers = None
	
	def __init__(self, *args, **kwargs):
		super(SendGridEmailMessage, self).__init__(*args, **kwargs)
		
	def _get_sendgrid_connection(self, backend=None):
		"""docstring for _get_sendgrid_connection"""
		logger.debug("Getting SendGrid connection")
		
		if not backend:
			backend = SENDGRID_EMAIL_BACKEND
			
		connection = mail.get_connection(backend)
		return connection
		
	def send(self, *args, **kwargs):
		"""Sends the email message."""
		connection = self._get_sendgrid_connection()
		self.connection = connection
		logger.debug("Connection: {c}".format(c=connection))
		
		response = super(SendGridEmailMessage, self).send(*args, **kwargs)
		sendgrid_email_sent.send(sender=self, email=self.message, response=response)
		
		return response
		