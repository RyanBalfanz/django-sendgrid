import logging

from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sendgrid.signals import sendgrid_email_sent


DEFAULT_SENDGRID_EMAIL_TRACKING_COMPONENTS = (
	"to",
	"cc",
	"bcc",
	"subject",
	"body",
	"extra_headers",
	"attachments",
)

SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)
SENDGRID_EMAIL_TRACKING = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)
SENDGRID_EMAIL_TRACKING_COMPONENTS = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", DEFAULT_SENDGRID_EMAIL_TRACKING_COMPONENTS)

EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH = 150
EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH = 150

if SENDGRID_USER_MIXIN_ENABLED:
	from django.contrib.auth.models import User
	from sendgrid.mixins import SendGridUserMixin
	
	User.__bases__ += (SendGridUserMixin,)

logger = logging.getLogger(__name__)

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
		"extra_headers": EmailMessageExtraHeadersData,
		"attachments": EmailMessageAttachmentsData,
	}

	if SENDGRID_EMAIL_TRACKING:
		messageId = getattr(message, "_message_id", None) # TODO: Fix _message_id access
		fromEmail = getattr(message, "from_email", None)
		recipients = getattr(message, "to", None) # TODO: Handle multiple recipients
		toEmail = recipients[0]

		emailMessage = EmailMessage.objects.create(
			message_id=messageId,
			from_email=fromEmail,
			to_email=toEmail,
			response=response,
		)

		for component, componentModel in COMPONENT_DATA_MODEL_MAP.iteritems():
			if component in SENDGRID_EMAIL_TRACKING_COMPONENTS:
				componentData = getattr(message, component, None)
				if componentData:
					componentData = componentModel.objects.create(
						email_message=emailMessage,
						data=componentData,
					)
			else:
				logMessage = "Component {c} is not tracked"
				logger.debug(logMEssage.format(c=component))


class EmailMessage(models.Model):
	message_id = models.CharField(unique=True, max_length=36, editable=False, blank=True)
	from_email = models.CharField(max_length=EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH)
	to_email = models.CharField(max_length=EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH)
	response = models.IntegerField(blank=True, null=True)
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


class EmailMessageExtraHeadersData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="extra_headers")
	data = models.TextField(_("Extra Headers"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageExtraHeadersData")
		verbose_name_plural = _("EmailMessageExtraHeadersDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBodyData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="body")
	data = models.TextField(_("Body"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageBodyData")
		verbose_name_plural = _("EmailMessageBodyDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageAttachmentsData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="attachments")
	data = models.TextField(_("Attachments"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageAttachmentData")
		verbose_name_plural = _("EmailMessageAttachmentsDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBccData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="bcc")
	data = models.TextField(_("Blind Carbon Copies"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageBccData")
		verbose_name_plural = _("EmailMessageBccDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageCcData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="cc")
	data = models.TextField(_("Carbon Copies"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageCcData")
		verbose_name_plural = _("EmailMessageCcDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageToData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="to")
	data = models.TextField(_("To"), editable=False) # TODO: JSONField, __getattr__

	class Meta:
		verbose_name = _("EmailMessageToData")
		verbose_name_plural = _("EmailMessageToDatas")

	def __unicode__(self):
		return "{0}".format(self.email_message)
