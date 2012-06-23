from __future__ import absolute_import

import datetime
import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .constants import EVENT_TYPES_MAP
from .signals import sendgrid_event_recieved
from .signals import sendgrid_event_processed


SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH = getattr(settings, "SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH", 255)
SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)

if SENDGRID_USER_MIXIN_ENABLED:
	from .mixins import SendGridUserMixin
	User.__bases__ += (SendGridUserMixin,)

logger = logging.getLogger(__name__)


@receiver(sendgrid_event_processed)
def handle_sendgrid_event(sender, **kwargs):
	logger.debug("SendGrid event recieved!")

	eventDetail = kwargs["detail"]

	email = eventDetail["email"]
	event = eventDetail["event"]
	try:
		category = eventDetail["category"]
		uniqueArgs = eventDetail["unique_args"]
		message_id = uniqueArgs["message_id"]
	except KeyError as e:
		logger.exception("Caught KeyError: {error}".format(error=e))
		return

	emailMessage, created = SendGridEmailMessage.objects.get_or_create(message_id=message_id)
	if created:
		logger.info("Created {obj}".format(obj=emailMessage))

	sendgridEvent = SendGridEvent.objects.create(
		email_message=emailMessage,
		type=EVENT_TYPES_MAP[event.upper()],
	)


class SendGridEvent(models.Model):
	SENDGRID_EVENT_UNKNOWN_TYPE = EVENT_TYPES_MAP["UNKNOWN"]
	SENDGRID_EVENT_DEFERRED_TYPE = EVENT_TYPES_MAP["DEFERRED"]
	SENDGRID_EVENT_PROCESSED_TYPE = EVENT_TYPES_MAP["PROCESSED"]
	SENDGRID_EVENT_DROPPED_TYPE = EVENT_TYPES_MAP["DROPPED"]
	SENDGRID_EVENT_DELIVERED_TYPE = EVENT_TYPES_MAP["DELIVERED"]
	SENDGRID_EVENT_BOUNCE_TYPE = EVENT_TYPES_MAP["BOUNCED"]
	SENDGRID_EVENT_OPEN_TYPE = EVENT_TYPES_MAP["OPENED"]
	SENDGRID_EVENT_CLICK_TYPE = EVENT_TYPES_MAP["CLICKED"]
	SENDGRID_EVENT_SPAM_REPORT_TYPE = EVENT_TYPES_MAP["SPAMREPORT"]
	SENDGRID_EVENT_UNSUBSCRIBE_TYPE = EVENT_TYPES_MAP["UNSUBSCRIBED"]
	SENDGRID_EVENT_TYPES = (
		(SENDGRID_EVENT_UNKNOWN_TYPE, "Unknown"),
		(SENDGRID_EVENT_DEFERRED_TYPE, "Deferred"),
		(SENDGRID_EVENT_PROCESSED_TYPE, "Processed"),
		(SENDGRID_EVENT_DROPPED_TYPE, "Dropped"),
		(SENDGRID_EVENT_DELIVERED_TYPE, "Delivered"),
		(SENDGRID_EVENT_BOUNCE_TYPE, "Bounce"),
		(SENDGRID_EVENT_OPEN_TYPE, "Open"),
		(SENDGRID_EVENT_CLICK_TYPE, "Click"),
		(SENDGRID_EVENT_SPAM_REPORT_TYPE, "Spam Report"),
		(SENDGRID_EVENT_UNSUBSCRIBE_TYPE, "Unsubscribe"),
	)
	creation_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	
	type = models.IntegerField(blank=True, null=True, choices=SENDGRID_EVENT_TYPES, default=SENDGRID_EVENT_UNKNOWN_TYPE)
	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)

	def __unicode__(self):
		return u"{} - {}".format(self.email_message, self.get_type_display())
	
	def save(self, *args, **kwargs):
		self.last_modified_time = datetime.datetime.now()
		super(SendGridEvent, self).save(*args, **kwargs)
