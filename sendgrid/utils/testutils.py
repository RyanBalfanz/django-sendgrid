from django.test.client import Client
from sendgrid.constants import EVENT_TYPES_EXTRA_FIELDS_MAP
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

client = Client()
def post_test_event(event_type,event_model_name,email_message):
	event_data = {
		"event": event_type,
		"message_id": email_message.message_id,
		"email": email_message.to_email
	}

	for key in EVENT_TYPES_EXTRA_FIELDS_MAP[event_type.upper()]:
		print "Adding Extra Field {0}".format(key)
		if key == "attempt":
			event_data[key] = 3
		else:
			event_data[key] = "test_param" + key

	return client.post(reverse("sendgrid_post_event",args=[]),data=urlencode(event_data),content_type="application/x-www-form-urlencoded; charset=utf-8")