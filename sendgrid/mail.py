import logging

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import send_mail

# django-sendgrid
from utils import in_test_environment


SENDGRID_EMAIL_BACKEND = getattr(settings, "SENDGRID_EMAIL_BACKEND", None)

logger = logging.getLogger(__name__)

def get_sendgrid_connection(*args, **kwargs):
	"""
	Returns an instance of the email backend specified in SENDGRID_EMAIL_BACKEND.
	"""
	backend = SENDGRID_EMAIL_BACKEND
	# if in_test_environment:
	# 	logger.debug("In test environment!")
	# 	backend = 'django.core.mail.backends.locmem.EmailBackend'
		
	logger.debug("Getting SendGrid connection using backend {b}".format(b=backend))
	sendgrid_connection = get_connection(backend, *args, **kwargs)
	
	return sendgrid_connection

def send_sendgrid_mail(subject, message, from_email, recipient_list,
	fail_silently=False, auth_user=None, auth_password=None, connection=None):
	"""
	Sends mail with SendGrid.
	"""
	sendgrid_connection = get_sendgrid_connection()
	return send_mail(subject, message, from_email, recipient_list,
		fail_silently, auth_user, auth_password, connection=sendgrid_connection)

def send_mass_sendgrid_mail(datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None):
	"""
	Sends mass mail with SendGrid.
	"""
	raise NotImplementedError
	
	sendgrid_connection = get_sendgrid_connection()
	return send_mass_mail(datatuple, fail_silently, auth_password, auth_password, connection=sendgrid_connection)
