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

Add ``sendgrid`` to your ``INSTALLED_APPS``::

	INSTALLED_APPS = (
		# Existing apps
		"sendgrid",
	)

Add the following to your ``settings``::

	SENDGRID_EMAIL_HOST = "smtp.sendgrid.net"
	SENDGRID_EMAIL_PORT = 587
	SENDGRID_EMAIL_USERNAME = "your_sendgrid_username"
	SENDGRID_EMAIL_PASSWORD = "your_sendgrid_password"

The API is similar to that of Django's; create a ``SendGridEmailMessage`` and send it::
	
	>>> from sendgrid.message import SendGridEmailMessage
	>>> email = SendGridEmailMessage('Subject', 'Body', 'ryan@ryanbalfanz.net', ['ryan@ryanbalfanz.net'])
	>>> email.send()
