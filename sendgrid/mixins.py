from django.conf import settings
from django.utils import simplejson

from utils import add_unsubscribes
from utils import delete_unsubscribes
from utils import get_unsubscribes


SENDGRID_EMAIL_USERNAME = getattr(settings, "SENDGRID_EMAIL_USERNAME", None)
SENDGRID_EMAIL_PASSWORD = getattr(settings, "SENDGRID_EMAIL_PASSWORD", None)


class SendGridUserMixin:
	"""
	Adds SendGrid related convienence functions and properties to ``User`` objects.
	"""
	def is_unsubscribed(self):
		"""
		Returns True if the ``User``.``email`` belongs to the unsubscribe list.
		"""
		response = get_unsubscribes(email=self.email)
		results = simplejson.loads(response)
		return len(results) > 0
		
	def add_to_unsubscribes(self):
		"""
		Adds the ``User``.``email`` from the unsubscribe list.
		"""
		response = add_unsubscribes(email=self.email)
		result = simplejson.loads(response)
		return result
		
	def delete_from_unsubscribes(self):
		"""
		Removes the ``User``.``email`` from the unsubscribe list.
		"""
		response = delete_unsubscribes(email=self.email)
		result = simplejson.loads(response)
		return result
