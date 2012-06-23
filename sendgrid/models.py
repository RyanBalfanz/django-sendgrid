from __future__ import absolute_import

import datetime
import logging

import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .constants import EVENT_TYPES_MAP
from .signals import sendgrid_email_sent
from .signals import sendgrid_event_recieved
from .signals import sendgrid_event_processed


DEFAULT_SENDGRID_EMAIL_TRACKING_COMPONENTS = (
	"to",
	"cc",
	"bcc",
	"subject",
	"body",
	"sendgrid_headers",
	"extra_headers",
	"attachments",
)

SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH = getattr(settings, "SENDGRID_EMAIL_MESSAGE_MAX_SUBJECT_LENGTH", 255)
SENDGRID_EMAIL_TRACKING = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)
SENDGRID_EMAIL_TRACKING_COMPONENTS = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", DEFAULT_SENDGRID_EMAIL_TRACKING_COMPONENTS)

EMAIL_MESSAGE_CATEGORY_MAX_LENGTH = 150

# To store all possible valid email addresses, a max_length of 254 is required.
# See RFC3696/5321
EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH = 254
EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH = 254

SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)
if SENDGRID_USER_MIXIN_ENABLED:
	from django.contrib.auth.models import User
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

@receiver(sendgrid_email_sent)
def save_email_message(sender, **kwargs):
	message = kwargs.get("message", None)
	response = kwargs.get("response", None)

	COMPONENT_DATA_MODEL_MAP = {
		"to": EmailMessageToData,
		"cc": EmailMessageCcData,
		"bcc": EmailMessageBccData,
		"subject": EmailMessageSubjectData,
		"body": EmailMessageBodyData,
		"sendgrid_headers": EmailMessageSendGridHeadersData,
		"extra_headers": EmailMessageExtraHeadersData,
		"attachments": EmailMessageAttachmentsData,
	}

	if SENDGRID_EMAIL_TRACKING:
		messageId = getattr(message, "message_id", None)
		fromEmail = getattr(message, "from_email", None)
		recipients = getattr(message, "to", None)
		toEmail = recipients[0]
		category = message.sendgrid_headers.data.get("category", None)

		emailMessage = EmailMessage.objects.create(
			message_id=messageId,
			from_email=fromEmail,
			to_email=toEmail,
			category=category,
			response=response,
		)

		for component, componentModel in COMPONENT_DATA_MODEL_MAP.iteritems():
			if component in SENDGRID_EMAIL_TRACKING_COMPONENTS:
				if component == "sendgrid_headers":
					componentData = message.sendgrid_headers.as_string()
				else:
					componentData = getattr(message, component, None)

				if componentData:
					componentData = componentModel.objects.create(
						email_message=emailMessage,
						data=componentData,
					)
				else:
					logger.debug("Could not get data for '{c}' component: {d}".format(c=component, d=componentData))
			else:
				logMessage = "Component {c} is not tracked"
				logger.debug(logMessage.format(c=component))


class EmailMessage(models.Model):
	message_id = models.CharField(unique=True, max_length=36, editable=False, blank=True, null=True, help_text="UUID")
	# user = models.ForeignKey(User, null=True) # TODO
	from_email = models.CharField(max_length=EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH, help_text="Sender's e-mail")
	to_email = models.CharField(max_length=EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH, help_text="Primiary recipient's e-mail")
	category = models.CharField(max_length=EMAIL_MESSAGE_CATEGORY_MAX_LENGTH, blank=True, null=True, help_text="SendGrid category")
	response = models.IntegerField(blank=True, null=True, help_text="Response received from SendGrid after sending")
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("EmailMessage")
		verbose_name_plural = _("EmailMessages")

	def __unicode__(self):
		return "{0}".format(self.message_id)

	def get_to_data(self):
		return self.to.data
	to_data = property(get_to_data)

	def get_cc_data(self):
		return self.to.data
	cc_data = property(get_cc_data)

	def get_bcc_data(self):
		return self.to.data
	bcc_data = property(get_bcc_data)

	def get_subject_data(self):
		return self.subject.data
	subject_data = property(get_subject_data)

	def get_body_data(self):
		return self.subject.data
	body_data = property(get_body_data)

	def get_extra_headers_data(self):
		return self.headers.data
	extra_headers_data = property(get_extra_headers_data)

	def get_attachments_data(self):
		return self.headers.data
	attachments_data = property(get_attachments_data)


class EmailMessageSubjectData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="subject")
	data = models.TextField(_("Subject"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageSubjectData")
		verbose_name_plural = _("EmailMessageSubjectDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageSendGridHeadersData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="sendgrid_headers")
	data = models.TextField(_("SendGrid Headers"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageSendGridHeadersData")
		verbose_name_plural = _("EmailMessageSendGridHeadersDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageExtraHeadersData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="extra_headers")
	data = models.TextField(_("Extra Headers"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageExtraHeadersData")
		verbose_name_plural = _("EmailMessageExtraHeadersDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBodyData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="body")
	data = models.TextField(_("Body"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageBodyData")
		verbose_name_plural = _("EmailMessageBodyDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageAttachmentsData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="attachments")
	data = models.TextField(_("Attachments"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageAttachmentData")
		verbose_name_plural = _("EmailMessageAttachmentsDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBccData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="bcc")
	data = models.TextField(_("Blind Carbon Copies"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageBccData")
		verbose_name_plural = _("EmailMessageBccDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageCcData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="cc")
	data = models.TextField(_("Carbon Copies"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageCcData")
		verbose_name_plural = _("EmailMessageCcDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageToData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="to")
	data = models.TextField(_("To"), editable=False)

	class Meta:
		verbose_name = _("EmailMessageToData")
		verbose_name_plural = _("EmailMessageToDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


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
	email_message = models.ForeignKey(EmailMessage)
	type = models.IntegerField(blank=True, null=True, choices=SENDGRID_EVENT_TYPES, default=SENDGRID_EVENT_UNKNOWN_TYPE)
	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)

	def __unicode__(self):
		return u"{} - {}".format(self.email_message, self.get_type_display())
	
	def save(self, *args, **kwargs):
		self.last_modified_time = datetime.datetime.now()
		super(SendGridEvent, self).save(*args, **kwargs)
