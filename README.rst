===============
django-sendgrid
===============

.. image:: https://pypip.in/d/django-sendgrid/badge.png

Master Branch Build Status:

.. image:: https://www.codeship.io/projects/64b8c9d0-8f52-0130-fe63-22000a95225b/status?branch=master

Develop Branch Build Status:

.. image:: https://www.codeship.io/projects/64b8c9d0-8f52-0130-fe63-22000a95225b/status?branch=develop


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

Don't forget to migrate::

	python manage.py migrate sendgrid

The API is similar to that of Django's; create a ``SendGridEmailMessage`` and send it::

	>>> from sendgrid.message import SendGridEmailMessage
	>>> email = SendGridEmailMessage('Subject', 'Body', 'ryan@ryanbalfanz.net', ['ryan@ryanbalfanz.net'])
	>>> email.send()


Additional Information
----------------------

 - https://docs.djangoproject.com/en/1.3/topics/email/
 - http://ryanbalfanz.github.com/django-sendgrid/
 - http://pypi.python.org/pypi/django-sendgrid
 - http://djangopackages.com/packages/p/django-sendgrid/

Preview
-------

List View

.. image:: https://s3.amazonaws.com/django-sendgrid/email_message_list.png

Detail View

.. image:: https://s3.amazonaws.com/django-sendgrid/email_message_detail.png
