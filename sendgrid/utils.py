def in_test_environment():
	"""
	Returns True if in a test environment, False otherwise.
	"""
	from django.core import mail
	
	return hasattr(mail, 'outbox')
