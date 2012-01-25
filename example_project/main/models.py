import logging

from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# django-sendgrid
from sendgrid.mail import get_sendgrid_connection
from sendgrid.mail import send_sendgrid_mail


logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def send_new_user_email(sender, instance, created, raw, using, **kwargs):
	if created:
		send_sendgrid_mail(
			subject="Your new account!",
			message="Thanks for signing up.",
			from_email='welcome@example.com',
			recipient_list=[instance.username],
		)
