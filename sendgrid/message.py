from __future__ import absolute_import

# import datetime
import logging
import time
import uuid
try:
	import simplejson as json
except ImportError:
	import json

from django.conf import settings
from django.core import mail
from django.core.mail.message import EmailMessage
from django.core.mail.message import EmailMultiAlternatives

# django-sendgrid imports
from .header import SmtpApiHeader
from .mail import get_sendgrid_connection
from .signals import sendgrid_email_sent


logger = logging.getLogger(__name__)


class SendGridEmailMessageMixin:
	"""
	Adds support for SendGrid features.
	"""
	def _update_headers_with_sendgrid_headers(self):
		"""
		Updates the existing headers to include SendGrid headers.
		"""
		logger.debug("Updating headers with SendGrid headers")
		if self.sendgrid_headers:
			additionalHeaders = {
				"X-SMTPAPI": self.sendgrid_headers.asJSON()
			}
			self.extra_headers.update(additionalHeaders)

		logging.debug(str(self.extra_headers))

		return self.extra_headers
		
	def _update_unique_args(self, uniqueArgs):
		"""docstring for _update_unique_args"""
		oldUniqueArgs = self.sendgrid_headers.data.get("unique_args", None)
		newUniquieArgs = oldUniqueArgs.copy() if oldUniqueArgs else {}
		newUniquieArgs.update(uniqueArgs)
		self.sendgrid_headers.setUniqueArgs(newUniquieArgs)

		return self.sendgrid_headers.data["unique_args"]

	def update_headers(self, *args, **kwargs):
		"""
		Updates the headers.
		"""
		return self._update_headers_with_sendgrid_headers(*args, **kwargs)
		
	def get_category(self):
		"""docstring for get_category"""
		return self.sendgrid_headers.data["category"]
	category = property(get_category)

	def get_unique_args(self):
		"""docstring for get_unique_args"""
		return self.sendgrid_headers.data.get("unique_args", None)
	unique_args = property(get_unique_args)
	
	def setup_connection(self):
		"""docstring for setup_connection"""
		# Set up the connection
		connection = get_sendgrid_connection()
		self.connection = connection
		logger.debug("Connection: {c}".format(c=connection))
	
	def prep_message_for_sending(self):
		"""docstring for prep_message_for_sending"""
		self.setup_connection()
		
		# now = tz.localize(datetime.datetime.strptime(timestamp[:26], POSTMARK_DATETIME_STRING)).astimezone(pytz.utc)
		uniqueArgs = {
			"message_id": str(self._message_id),
			# "submition_time": time.time(),
		}
		self._update_unique_args(uniqueArgs)
		
		self.update_headers()

	def get_message_id(self):
		return self._message_id
	message_id = property(get_message_id)


class SendGridEmailMessage(SendGridEmailMessageMixin, EmailMessage):
	"""
	Adapts Django's ``EmailMessage`` for use with SendGrid.
	
	>>> from sendgrid.message import SendGridEmailMessage
	>>> myEmail = "rbalfanz@gmail.com"
	>>> mySendGridCategory = "django-sendgrid"
	>>> e = SendGridEmailMessage("Subject", "Message", myEmail, [myEmail], headers={"Reply-To": myEmail})
	>>> e.sendgrid_headers.setCategory(mySendGridCategory)
	>>> response = e.send()
	"""
	
	def __init__(self, *args, **kwargs):
		"""
		Initialize the object.
		"""
		self.sendgrid_headers = SmtpApiHeader()
		self._message_id = uuid.uuid4()
		super(SendGridEmailMessage, self).__init__(*args, **kwargs)
		
	def send(self, *args, **kwargs):
		"""Sends the email message."""
		self.prep_message_for_sending()
		
		response = super(SendGridEmailMessage, self).send(*args, **kwargs)
		logger.debug("Tried to send an email with SendGrid and got response {r}".format(r=response))
		sendgrid_email_sent.send(sender=self, message=self, response=response)
		
		return response

	def get_message_id(self):
		return self._message_id
	message_id = property(get_message_id)


class SendGridEmailMultiAlternatives(SendGridEmailMessageMixin, EmailMultiAlternatives):
	"""
	Adapts Django's ``EmailMultiAlternatives`` for use with SendGrid.
	"""
	
	def __init__(self, *args, **kwargs):
		self.sendgrid_headers = SmtpApiHeader()
		self._message_id = uuid.uuid4()
		super(SendGridEmailMultiAlternatives, self).__init__(*args, **kwargs)
		
	def send(self, *args, **kwargs):
		"""Sends the email message."""
		self.prep_message_for_sending()
		
		response = super(SendGridEmailMultiAlternatives, self).send(*args, **kwargs)
		logger.debug("Tried to send an email with SendGrid and got response {r}".format(r=response))
		sendgrid_email_sent.send(sender=self, message=self, response=response)

		return response
