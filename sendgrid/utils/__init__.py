import datetime
import httplib
import logging
import time
import urllib
import urllib2

from django.conf import settings
from django.core import mail

# from sendgrid.models import EmailMessage


SENDGRID_EMAIL_USERNAME = getattr(settings, "SENDGRID_EMAIL_USERNAME", None)
SENDGRID_EMAIL_PASSWORD = getattr(settings, "SENDGRID_EMAIL_PASSWORD", None)

logger = logging.getLogger(__name__)

# def get_email_message(key):
# 	if isinstance(key, EmailMessage):
# 		emailMessage = key
# 	elif isinstance(key, int):
# 		emailMessage = EmailMessage.objects.get(id=key)
# 	elif isinstance(key, long):
# 		emailMessage = EmailMessage.objects.get(id=key)
# 	elif isinstance(key, basestring):
# 		emailMessage = EmailMessage.objects.get(message_id=key)
# 	else:
# 		raise ValueError

# 	return emailMessage

def in_test_environment():
	"""
	Returns True if in a test environment, False otherwise.
	"""
	return hasattr(mail, 'outbox')

def remove_keys_without_value(d):
	"""
	Removes all key-value pairs with empty values.
	"""
	dCopy = d.copy()
	
	delKeys = [k for k, v in dCopy.iteritems() if not v]
	for k in delKeys:
		del dCopy[k]
		
	return dCopy

def normalize_parameters(d):
	"""
	Normalizes the parameters, adds authorization details and removes empty entries.
	"""
	dCopy = d.copy()
	
	authorization = {
		"api_user": SENDGRID_EMAIL_USERNAME,
		"api_key": SENDGRID_EMAIL_PASSWORD,
	}
	dCopy.update(authorization)
	dCopy = remove_keys_without_value(dCopy)
	
	return dCopy

def get_unsubscribes(date=None, days=None, start_date=None, end_date=None, limit=None, offset=None, email=None):
	"""
	Returns a list of unsubscribes with addresses and optionally with dates.
	"""
	ENDPOINT = "https://sendgrid.com/api/unsubscribes.get.json"
	
	if days and (start_date or end_date):
		raise AttributeError
		
	if days:
		if start_date or end_date:
			raise AttributeError
	elif start_date and end_date:
		if days:
			raise AttributeError
			
	parameters = {
		"date": date,
		"days": days,
		"start_date": start_date,
		"end_date": end_date,
		"limit": limit,
		"offset": offset,
		"email": email,
	}
	parameters = normalize_parameters(parameters)
	
	data = urllib.urlencode(parameters)
	request = urllib2.Request(ENDPOINT, data)
	response = urllib2.urlopen(request)
	content = response.read()

	return content

def add_unsubscribes(email):
	"""
	Add email addresses to the Unsubscribe list.
	"""
	ENDPOINT = "https://sendgrid.com/api/unsubscribes.add.json"
	
	parameters = {
		"email": email,
	}
	parameters = normalize_parameters(parameters)
	
	data = urllib.urlencode(parameters)
	request = urllib2.Request(ENDPOINT, data)
	response = urllib2.urlopen(request)
	content = response.read()

	return content

def delete_unsubscribes(email, start_date=None, end_date=None):
	"""
	Delete an address from the Unsubscribe list. Please note that if no parameters are provided the ENTIRE list will be removed.
	"""
	ENDPOINT = "https://sendgrid.com/api/unsubscribes.delete.json"
	
	if not ((start_date and end_date) or email):
		raise Exception("You're about to delete the entire list!")

	parameters = {
		"start_date": start_date,
		"end_date": end_date,
		"email": email,
	}
	parameters = normalize_parameters(parameters)
	
	data = urllib.urlencode(parameters)
	request = urllib2.Request(ENDPOINT, data)
	response = urllib2.urlopen(request)
	content = response.read()

	return content
