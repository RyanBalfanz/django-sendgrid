import logging

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend


SENDGRID_EMAIL_HOST = getattr(settings, "SENDGRID_EMAIL_HOST", None)
SENDGRID_EMAIL_PORT = getattr(settings, "SENDGRID_EMAIL_PORT", None)
SENDGRID_EMAIL_USERNAME = getattr(settings, "SENDGRID_EMAIL_USERNAME", None)
SENDGRID_EMAIL_PASSWORD = getattr(settings, "SENDGRID_EMAIL_PASSWORD", None)

logger = logging.getLogger(__name__)


def check_settings():
	"""
	Checks that the required settings are available.
	"""
	allOk = True
	
	checks = {
		"SENDGRID_EMAIL_HOST": SENDGRID_EMAIL_HOST,
		"SENDGRID_EMAIL_PORT": SENDGRID_EMAIL_PORT,
		"SENDGRID_EMAIL_USERNAME": SENDGRID_EMAIL_USERNAME,
		"SENDGRID_EMAIL_PASSWORD": SENDGRID_EMAIL_PASSWORD,
	}
	
	for key, value in checks.iteritems():
		if not value:
			logger.warn("{k} is not set".format(k=key))
			allOk = False
			
	return allOk

class SendGridEmailBackend(EmailBackend):
	"""
	A wrapper that manages the SendGrid SMTP network connection.
	"""
	def __init__(self, host=None, port=None, username=None, password=None, use_tls=None, fail_silently=False, **kwargs):
		if not check_settings():
			raise ValueError("A required setting was not found")
			
		super(SendGridEmailBackend, self).__init__(
			host=SENDGRID_EMAIL_HOST,
			port=SENDGRID_EMAIL_PORT,
			username=SENDGRID_EMAIL_USERNAME,
			password=SENDGRID_EMAIL_PASSWORD,
			fail_silently=fail_silently,
		)
