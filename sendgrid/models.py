from __future__ import absolute_import

import datetime
import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .constants import EVENT_TYPES_MAP
from .signals import sendgrid_email_sent
from .signals import sendgrid_event_recieved
from .signals import sendgrid_event_processed


SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH = getattr(settings, "SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH", 255)
SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)

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

if SENDGRID_USER_MIXIN_ENABLED:
	from .mixins import SendGridUserMixin
	User.__bases__ += (SendGridUserMixin,)

logger = logging.getLogger(__name__)

@receiver(sendgrid_email_sent)
def create_sendgrid_email_message(sender, **kwargs):
	logger.debug("E-mail sent with SendGrid")
	
	msg = kwargs["message"]
	resp = kwargs["response"]

	emsg = SendGridEmailMessage(
		message_id=msg.message_id,
	)
	emsg.save()

@receiver(sendgrid_event_processed)
def handle_sendgrid_event(sender, **kwargs):
	logger.debug("SendGrid event recieved!")

	eventDetail = kwargs["detail"]

	email = eventDetail["email"]
	event = eventDetail["event"]
	category = eventDetail["category"]
	uniqueArgs = eventDetail["unique_args"]
	message_id = uniqueArgs["message_id"]

	emailMessage, created = SendGridEmailMessage.objects.get_or_create(message_id=message_id)
	if created:
		pass

	sendgridEvent = SendGridEvent.objects.create(
		email_message=emailMessage,
		type=EVENT_TYPES_MAP[event.upper()],
	)


class SendGridEmailMessage(models.Model):
	"""(SendGridEmailMessage description)"""
	message_id = models.CharField(blank=True, null=True, max_length=36) # Version 4 UUID
	creation_time = models.DateTimeField(blank=True, default=datetime.datetime.now)

	from_email = models.EmailField()
	recipient_email = models.EmailField()
	# recipient_email_list = JSONField(blank=True, null=True)
	# cc_email_list = JSONField(blank=True, null=True)
	# bcc_email_list = JSONField(blank=True, null=True)
	reply_to_email = models.EmailField(blank=True, null=True)

	subject = models.CharField("Subject", max_length=SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH)
	text_body = models.TextField("Text Body", blank=True, null=True)
	html_body = models.TextField("HTML Body", blank=True, null=True)

	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)

	# events = models.ManyToManyField(Event)

	class Meta:
		verbose_name = _("E-mail Message")
		verbose_name_plural = _("E-mail Messages")

	def __unicode__(self):
		return u"{}".format(self.message_id)

	def save(self, *args, **kwargs):
		self.last_modified_time = datetime.datetime.now()
		super(SendGridEmailMessage, self).save(*args, **kwargs)

	def get_event_count(self):
		return self.events.count()
	event_count = property(get_event_count)

	def get_latest_event(self):
		latestEvent = None
		if self.events.exists():
			self.events.all()[0]

		return latestEvent
	latest_event = property(get_latest_event)

	def get_latest_event_type(self):
		return self.get_latest_event().get_type_display() if self.get_event_count() > 0 else "No Events"
	status = property(get_latest_event_type)

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
	email_message = models.ForeignKey(SendGridEmailMessage, related_name="events", verbose_name="Email Message")
	creation_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	
	type = models.IntegerField(blank=True, null=True, choices=SENDGRID_EVENT_TYPES, default=SENDGRID_EVENT_UNKNOWN_TYPE)
	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)

	def __unicode__(self):
		return u"{} - {}".format(self.email_message, self.get_type_display())
	
	def save(self, *args, **kwargs):
		self.last_modified_time = datetime.datetime.now()
		super(SendGridEvent, self).save(*args, **kwargs)
