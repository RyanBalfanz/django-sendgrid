import logging

from django.contrib.auth.models import User
# from django.core.mail import get_connection
from django.core.mail import EmailMessage
# from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# django-sendgrid
# from sendgrid.mail import get_sendgrid_connection
from sendgrid.mail import send_sendgrid_mail
from sendgrid.mail import send_sendgrid_mail
from sendgrid.message import SendGridEmailMessage


logger = logging.getLogger(__name__)

REGISTRATION_EMAIL_SPEC = {
	"subject": "Your new account!",
	"body": "Thanks for signing up.",
	"from_email": 'welcome@example.com',
}

def get_user(user):
	"""docstring for get_user"""
	_user = None
	if isinstance(user, User):
		_user = user
	elif isinstance(user, basestring):
		try:
			user = int(user)
		except ValueError:
			try:
				_user = User.objects.get(username=user)
			except User.DoesNotExist as e:
				logger.exception("Caught exception: {error}".format(error=e))
		else:
			try:
				_user = User.objects.get(id=user)
			except User.DoesNotExist as e:
				logger.exception("Caught exception: {error}".format(error=e))
				
	return _user

def send_registration_email_to_new_user(user, emailOptions=REGISTRATION_EMAIL_SPEC):
	"""
	Sends a registration email to ``user``.
	"""
	user = get_user(user)
	
	registrationEmail = SendGridEmailMessage(
		to=[user.username],
		**emailOptions
	)
	registrationEmail.sendgrid_headers.setCategory("Registration")
	response = registrationEmail.send()
	
	return response

@receiver(post_save, sender=User)
def send_new_user_email(sender, instance, created, raw, using, **kwargs):
	logger.debug("Received post_save from {user}".format(user=instance))
	if created:
		# Send a custom email, with, for example, a category.
		send_registration_email_to_new_user(instance)
		
		# Send directly using ``send_sendgrid_mail`` shortcut.
		# send_sendgrid_mail(
		# 	recipient_list=[instance.username],
		# 	subject=REGISTRATION_EMAIL_SPEC["subject"],
		# 	message=REGISTRATION_EMAIL_SPEC["body"],
		# 	from_email=REGISTRATION_EMAIL_SPEC["from_email"],
		# )
