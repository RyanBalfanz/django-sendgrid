from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def send_new_user_email(sender, instance, created, raw, using, **kwargs):
	if created:
		connection = get_connection("sendgrid.backends.SendGridEmailBackend")
		
		email = EmailMessage(
			subject="Your new account!",
			body="Thanks for signing up.",
			from_email='welcome@example.com',
			to=[instance.email],
			connection=connection,
		)
		email.send()
