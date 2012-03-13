from django.conf import settings

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
		result = get_unsubscribes(email=self.email)
		return result
		
	def add_to_unsubscribes(self):
		"""
		Adds the ``User``.``email`` from the unsubscribe list.
		"""
		result = add_unsubscribes(email=self.email)
		return result
		
	def delete_from_unsubscribes(self):
		"""
		Removes the ``User``.``email`` from the unsubscribe list.
		"""
		result = delete_unsubscribes(email=self.email)
		return result
