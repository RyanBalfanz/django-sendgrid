from django.core.mail import get_connection
from django.core.mail import EmailMessage, send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def send_email_with_sendgrid(subject, message, from_email, recipient_list,
	fail_silently=False, auth_user=None, auth_password=None, connection=None):
	"""
	A wrapper for sending emails with ``sendgrid.backends.SendGridEmailBackend``.
	"""
	sendgrid_connection = get_connection("sendgrid.backends.SendGridEmailBackend")
	return send_mail(subject, message, from_email, recipient_list,
		fail_silently=False, auth_user=None, auth_password=None, connection=sendgrid_connection)
