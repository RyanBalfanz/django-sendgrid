===============
django-sendgrid
===============

django-sendgrid is the easiest way to send e-mail with SendGrid. It uses the SendGrid SMTP API, as recommended.

Although it's rather simple to use, a example project is included to demonstrate usage.

Installation
------------

To install with PyPi::

	pip install django-sendgrid


Usage
-----

Add the following to your ``settings``::

	SENDGRID_EMAIL_HOST = "smtp.sendgrid.net"
	SENDGRID_EMAIL_PORT = 587
	SENDGRID_EMAIL_USERNAME = "your_sendgrid_username"
	SENDGRID_EMAIL_PASSWORD = "your_sendgrid_password"

Create an ``EmailMessage`` and send it::

	>>> from django.core.mail import get_connection
	>>> from django.core.mail import EmailMessage
	>>> conn = get_connection("sendgrid.backends.SendGridEmailBackend")
	>>> email = EmailMessage("Hello django-sendgrid!", "Made with Awesome Sauce!", 'you@example.com', ["your_friend@example.com"], connection=conn)
	>>> email.send()

Use the helper function ``send_email_with_sendgrid``::

	>>> from sendgrid.utils import send_email_with_sendgrid
	>>> send_email_with_sendgrid("Hello django-sendgrid!", "Made with Awesome Sauce!", 'you@example.com', ["your_friend@example.com"], connection=conn)
