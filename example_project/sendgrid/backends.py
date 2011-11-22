from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

SENDGIRD_USE_DEFAULTS = getattr(settings, "SENDGIRD_USE_DEFAULTS", False)
SENDGRID_DEFAULT_EMAIL_HOST = "smtp.sendgrid.net"
SENDGRID_DEFAULT_EMAIL_PORT = 587

SENDGRID_EMAIL_HOST = getattr(settings, "SENDGRID_EMAIL_HOST", None)
SENDGRID_EMAIL_PORT = getattr(settings, "SENDGRID_EMAIL_PORT", None)
SENDGRID_EMAIL_USERNAME = getattr(settings, "SENDGRID_EMAIL_USERNAME", None)
SENDGRID_EMAIL_PASSWORD = getattr(settings, "SENDGRID_EMAIL_PASSWORD", None)


class SendGridEmailBackend(EmailBackend):
	"""
	A wrapper that manages the SendGrid SMTP network connection.
	"""
	def __init__(self, host=None, port=None, username=None, password=None, use_tls=None, fail_silently=False, **kwargs):
		# if not SENDGRID_EMAIL_HOST and SENDGIRD_USE_DEFAULTS:
		# 	SENDGRID_EMAIL_HOST = SENDGRID_DEFAULT_EMAIL_HOST
			
		# if not SENDGRID_EMAIL_PORT and SENDGIRD_USE_DEFAULTS:
		# 	SENDGRID_EMAIL_PORT = SENDGRID_DEFAULT_EMAIL_PORT
			
		super(SendGridEmailBackend, self).__init__(
			host=SENDGRID_EMAIL_HOST,
			port=SENDGRID_EMAIL_PORT,
			username=SENDGRID_EMAIL_USERNAME,
			password=SENDGRID_EMAIL_PASSWORD,
			fail_silently=fail_silently,
		)
