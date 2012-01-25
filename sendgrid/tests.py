"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from collections import defaultdict

from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.test import TestCase

# django-sendgrid
from mail import get_sendgrid_connection
from mail import send_sendgrid_mail
from message import SendGridEmailMessage
from signals import sendgrid_email_sent


class SendWithSendGridEmailMessageTest(TestCase):
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.signalsReceived = defaultdict(list)
		
	def test_send_email_sends_signal(self):
		"""
		Tests that sending a ``SendGridEmailMessage`` sends a ``sendgrid_email_sent`` signal.
		"""
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.signalsReceived["sendgrid_email_sent"].append(1)
			return True
			
		email = SendGridEmailMessage()
		email.send()
		
		numEmailSentSignalsRecieved = sum(self.signalsReceived["sendgrid_email_sent"])
		self.assertEqual(numEmailSentSignalsRecieved, 1)
		
	def test_send_with_send_mail(self):
		"""
		Tests sending an email with the ``send_email_with_sendgrid`` helper.
		"""
		send_sendgrid_mail(
			subject="Your new account!",
			message="Thanks for signing up.",
			from_email='welcome@example.com',
			recipient_list=['ryan@example.com'],
		)


class SendWithEmailMessageTest(TestCase):
	"""docstring for SendWithEmailMessageTest"""
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.connection = get_sendgrid_connection()
		
	def test_send_with_email_message(self):
		"""
		Tests sending an ``EmailMessage`` with the ``SendGridEmailBackend``.
		"""
		email = EmailMessage(
			subject="Your new account!",
			body="Thanks for signing up.",
			from_email='welcome@example.com',
			to=['ryan@example.com'],
			connection=self.connection,
		)
		email.send()
		