from __future__ import absolute_import

import datetime
import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .signals import sendgrid_email_sent, sendgrid_event_recieved


SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH = getattr(settings, "SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH", 255)
SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)

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

@receiver(sendgrid_event_recieved)
def handle_sendgrid_event(sender, **kwargs):
	logger.debug("SendGrid event recieved!")

	# event = SendGridEvent()
	# event.save()


class SendGridEmailMessage(models.Model):
	"""(SendGridEmailMessage description)"""
	SENDGRID_EMAIL_MESSAGE_UNKNOWN_TYPE = 0
	# Process
	SENDGRID_EMAIL_MESSAGE_PROCESSED_TYPE = 1000
	SENDGRID_EVENT_DROPPED_TYPE = 1000
	# Deliver
	SENDGRID_EVENT_DELIVERED_TYPE = 2000
	SENDGRID_EVENT_DEFERRED_TYPE = 2000
	SENDGRID_EVENT_BOUNCE_TYPE = 2000
	# Read
	SENDGRID_EVENT_OPEN_TYPE = 3000
	SENDGRID_EVENT_CLICK_TYPE = 3000
	SENDGRID_EVENT_SPAM_REPORT_TYPE = 3000
	SENDGRID_EVENT_UNSUBSCRIBE_TYPE = 3000

	SENDGRID_EMAIL_MESSAGE_STATUS_TYPES = (
		(SENDGRID_EMAIL_MESSAGE_UNKNOWN_TYPE, "Unknown"),
		(SENDGRID_EMAIL_MESSAGE_PROCESSED_TYPE, "Processed"),
		(SENDGRID_EVENT_DROPPED_TYPE, "Dropped"),
		(SENDGRID_EVENT_DELIVERED_TYPE, "Delivered"),
		(SENDGRID_EVENT_DEFERRED_TYPE, "Deferred"),
		(SENDGRID_EVENT_BOUNCE_TYPE, "Bounced"),
		(SENDGRID_EVENT_OPEN_TYPE, "Opened"),
		(SENDGRID_EVENT_CLICK_TYPE, "Clicked"),
		(SENDGRID_EVENT_SPAM_REPORT_TYPE, "Reported as span"),
		(SENDGRID_EVENT_UNSUBSCRIBE_TYPE, "Unsubscribed"),
	)

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

	status = models.IntegerField("Status", choices=SENDGRID_EMAIL_MESSAGE_STATUS_TYPES, default=SENDGRID_EMAIL_MESSAGE_UNKNOWN_TYPE)
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

class SendGridEvent(models.Model):
	# Received
	SENDGRID_EVENT_UNKNOWN_TYPE = 0
	# SENDGRID_EVENT_RECEIVED_TYPE = 1000
	# Process
	SENDGRID_EVENT_PROCESSED_TYPE = 1100
	SENDGRID_EVENT_DROPPED_TYPE = 1200
	# Deliver
	SENDGRID_EVENT_DELIVERED_TYPE = 2100
	SENDGRID_EVENT_DEFERRED_TYPE = 2200
	SENDGRID_EVENT_BOUNCE_TYPE = 2300
	# Read
	SENDGRID_EVENT_OPEN_TYPE = 3100
	SENDGRID_EVENT_CLICK_TYPE = 3200
	SENDGRID_EVENT_SPAM_REPORT_TYPE = 3300
	SENDGRID_EVENT_UNSUBSCRIBE_TYPE = 3400
	SENDGRID_EVENT_TYPES = (
		(SENDGRID_EVENT_UNKNOWN_TYPE, "Unknown"),
		(SENDGRID_EVENT_PROCESSED_TYPE, "Processed"),
		(SENDGRID_EVENT_DROPPED_TYPE, "Dropped"),
		(SENDGRID_EVENT_DELIVERED_TYPE, "Delivered"),
		(SENDGRID_EVENT_DEFERRED_TYPE, "Deferred"),
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
