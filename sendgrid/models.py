from __future__ import absolute_import

import datetime
import logging

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from six import string_types

from .signals import sendgrid_email_sent
from .signals import sendgrid_event_recieved
from sendgrid.constants import (
	ARGUMENT_DATA_TYPE_UNKNOWN,
	ARGUMENT_DATA_TYPE_BOOLEAN,
	ARGUMENT_DATA_TYPE_INTEGER,
	ARGUMENT_DATA_TYPE_FLOAT,
	ARGUMENT_DATA_TYPE_COMPLEX,
	ARGUMENT_DATA_TYPE_STRING,
	UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID,
)
from sendgrid.signals import sendgrid_email_sent

MAX_CATEGORIES_PER_EMAIL_MESSAGE = 10

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

SENDGRID_EMAIL_TRACKING = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)
SENDGRID_EMAIL_TRACKING_COMPONENTS = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", DEFAULT_SENDGRID_EMAIL_TRACKING_COMPONENTS)
SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)

ARGUMENT_KEY_MAX_LENGTH = 255
EMAIL_MESSAGE_CATEGORY_MAX_LENGTH = 150
EVENT_NAME_MAX_LENGTH = 128
UNIQUE_ARGUMENT_DATA_MAX_LENGTH = 255

# To store all possible valid email addresses, a max_length of 254 is required.
# See RFC3696/5321
EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH = 254
EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH = 254

if SENDGRID_USER_MIXIN_ENABLED:
	from django.contrib.auth.models import User
	from .mixins import SendGridUserMixin

	User.__bases__ += (SendGridUserMixin,)

logger = logging.getLogger(__name__)

@receiver(sendgrid_email_sent)
def update_email_message(sender, message, response, **kwargs):
	messageId = getattr(message, "message_id", None)
	emailMessage = EmailMessage.objects.get(message_id=messageId)
	emailMessage.response = response
	emailMessage.save()

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
		categoryData = message.sendgrid_headers.data.get("category", None)
		if isinstance(categoryData, string_types):
			category = categoryData
			categories = [category]
		else:
			categories = categoryData
			category = categories[0] if categories else None

		if categories and len(categories) > MAX_CATEGORIES_PER_EMAIL_MESSAGE:
			msg = "The message has {n} categories which exceeds the maximum of {m}"
			logger.warn(msg.format(n=len(categories), m=MAX_CATEGORIES_PER_EMAIL_MESSAGE))

		emailMessage = EmailMessage.objects.create(
			message_id=messageId,
			from_email=fromEmail,
			to_email=toEmail,
			category=category,
			response=response,
		)

		if categories:
			for categoryName in categories:
				category, created = Category.objects.get_or_create(name=categoryName)
				if created:
					logger.debug("Category {c} was created".format(c=category))
				emailMessage.categories.add(category)

		uniqueArgsData = message.sendgrid_headers.data.get("unique_args", None)
		if uniqueArgsData:
			for k, v in uniqueArgsData.items():
				argument, argumentCreated = Argument.objects.get_or_create(key=k)
				if argumentCreated:
					logger.debug("Argument {a} was created".format(a=argument))
				uniqueArg = UniqueArgument.objects.create(
					argument=argument,
					email_message=emailMessage,
					data=v,
				)

		for component, componentModel in COMPONENT_DATA_MODEL_MAP.items():
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

@receiver(sendgrid_event_recieved)
def log_event_recieved(sender, request, **kwargs):
	if settings.DEBUG:
		logger.debug("Recieved event request: {request}".format(request=request))


class Category(models.Model):
	name = models.CharField(unique=True, max_length=EMAIL_MESSAGE_CATEGORY_MAX_LENGTH)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("Category")
		verbose_name_plural = _("Categories")

	def __unicode__(self):
		return self.name


class Argument(models.Model):
	ARGUMENT_DATA_TYPE_UNKNOWN = ARGUMENT_DATA_TYPE_UNKNOWN
	ARGUMENT_DATA_TYPE_BOOLEAN = ARGUMENT_DATA_TYPE_BOOLEAN
	ARGUMENT_DATA_TYPE_INTEGER = ARGUMENT_DATA_TYPE_INTEGER
	ARGUMENT_DATA_TYPE_FLOAT = ARGUMENT_DATA_TYPE_FLOAT
	ARGUMENT_DATA_TYPE_COMPLEX = ARGUMENT_DATA_TYPE_COMPLEX
	ARGUMENT_DATA_TYPE_STRING = ARGUMENT_DATA_TYPE_STRING
	ARGUMENT_DATA_TYPES = (
		(ARGUMENT_DATA_TYPE_UNKNOWN, _("Unknown")),
		(ARGUMENT_DATA_TYPE_BOOLEAN, _("Boolean")),
		(ARGUMENT_DATA_TYPE_INTEGER, _("Integer")),
		(ARGUMENT_DATA_TYPE_FLOAT, _("Float")),
		(ARGUMENT_DATA_TYPE_COMPLEX, _("Complex")),
		(ARGUMENT_DATA_TYPE_STRING, _("String")),
	)
	key = models.CharField(max_length=ARGUMENT_KEY_MAX_LENGTH)
	data_type = models.IntegerField(_("Data Type"), choices=ARGUMENT_DATA_TYPES, default=ARGUMENT_DATA_TYPE_UNKNOWN)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("Argument")
		verbose_name_plural = _("Arguments")

	def __unicode__(self):
		return self.key


class EmailMessage(models.Model):
	message_id = models.CharField(unique=True, max_length=36, editable=False, blank=True, null=True, help_text="UUID")
	# user = models.ForeignKey(User, null=True) # TODO
	from_email = models.CharField(max_length=EMAIL_MESSAGE_FROM_EMAIL_MAX_LENGTH, help_text="Sender's e-mail")
	to_email = models.CharField(max_length=EMAIL_MESSAGE_TO_EMAIL_MAX_LENGTH, help_text="Primiary recipient's e-mail")
	category = models.CharField(max_length=EMAIL_MESSAGE_CATEGORY_MAX_LENGTH, blank=True, null=True, help_text="Primary SendGrid category")
	response = models.IntegerField(blank=True, null=True, help_text="Response received from SendGrid after sending")
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)
	categories = models.ManyToManyField(Category)
	arguments = models.ManyToManyField(Argument, through="UniqueArgument")

	class Meta:
		verbose_name = _("Email Message")
		verbose_name_plural = _("Email Messages")

	@classmethod
	def from_event(self, event_dict):
		"""
		Returns a new EmailMessage instance derived from an Event Dictionary.
		"""
		newsletter_id = event_dict.get("newsletter[newsletter_id]")
		to_email = event_dict.get("email")
		try:
			emailMessage = UniqueArgument.objects.get(data=newsletter_id, argument__key="newsletter[newsletter_id]", email_message__to_email=to_email).email_message
		except UniqueArgument.DoesNotExist:
			categories = [value for key,value in event_dict.items() if 'category' in key]
			emailMessageSpec = {
				"message_id": event_dict.get("message_id", None),
				"from_email": "",
				"to_email": to_email,
				"response": None
			}
			if len(categories) > 0:
				emailMessageSpec["category"] = categories[0]

			emailMessage = EmailMessage.objects.create(**emailMessageSpec)

			for category in categories:
				categoryObj,created = Category.objects.get_or_create(name=category)
				emailMessage.categories.add(categoryObj)

			uniqueArgs = {}
			for key in UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID:
				uniqueArgs[key] = event_dict.get(key)

			for argName, argValue in uniqueArgs.items():
				argument,_ = Argument.objects.get_or_create(
					key=argName
				)
				uniqueArg = UniqueArgument.objects.create(
					argument=argument,
					email_message=emailMessage,
					data=argValue
				)

		return emailMessage

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
		return self.body.data
	body_data = property(get_body_data)

	def get_extra_headers_data(self):
		return self.headers.data
	extra_headers_data = property(get_extra_headers_data)

	def get_attachments_data(self):
		try:
			data = self.attachments.data
		except EmailMessageAttachmentsData.DoesNotExist:
			data = None

		return data
	attachments_data = property(get_attachments_data)

	def get_event_count(self):
		return self.event_set.count()
	event_count = property(get_event_count)

	def get_first_event(self):
		events = self.event_set.all()
		if events.exists():
			firstEvent = events.order_by("creation_time")[0]
		else:
			firstEvent = None

		return firstEvent
	first_event = property(get_first_event)

	def get_latest_event(self):
		# If your model's Meta specifies get_latest_by,
		# you can leave off the field_name argument to latest()
		return self.event_set.latest("creation_time")
	latest_event = property(get_latest_event)


class UniqueArgument(models.Model):
	argument = models.ForeignKey(Argument)
	email_message = models.ForeignKey(EmailMessage)
	data = models.CharField(max_length=UNIQUE_ARGUMENT_DATA_MAX_LENGTH)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("Unique Argument")
		verbose_name_plural = _("Unique Arguments")

	def __unicode__(self):
		return "{key}: {value}".format(key=self.argument.key, value=self.value)

	def get_value(self):
		"""
		Returns data cast as the correct type.
		"""
		func_map = {
			ARGUMENT_DATA_TYPE_UNKNOWN: None,
			ARGUMENT_DATA_TYPE_BOOLEAN: bool,
			ARGUMENT_DATA_TYPE_INTEGER: int,
			ARGUMENT_DATA_TYPE_FLOAT: float,
			ARGUMENT_DATA_TYPE_COMPLEX: complex,
			ARGUMENT_DATA_TYPE_STRING: str,
		}
		f = func_map[self.argument.data_type]
		value = f(self.data) if f else self.data
		return value
	value = property(get_value)


class EmailMessageSubjectData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="subject")
	data = models.TextField(_("Subject"), editable=False)

	class Meta:
		verbose_name = _("Email Message Subject Data")
		verbose_name_plural = _("Email Message Subject Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageSendGridHeadersData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="sendgrid_headers")
	data = models.TextField(_("SendGrid Headers"), editable=False)

	class Meta:
		verbose_name = _("Email Message SendGrid Headers Data")
		verbose_name_plural = _("Email Message SendGrid Headers Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageExtraHeadersData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="extra_headers")
	data = models.TextField(_("Extra Headers"), editable=False)

	class Meta:
		verbose_name = _("Email Message Extra Headers Data")
		verbose_name_plural = _("Email Message Extra Headers Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBodyData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="body")
	data = models.TextField(_("Body"), editable=False)

	class Meta:
		verbose_name = _("Email Message Body Data")
		verbose_name_plural = _("Email Message Body Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageAttachmentsData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="attachments")
	data = models.TextField(_("Attachments"), editable=False)

	class Meta:
		verbose_name = _("Email Message Attachment Data")
		verbose_name_plural = _("Email Message Attachments Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageBccData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="bcc")
	data = models.TextField(_("Blind Carbon Copies"), editable=False)

	class Meta:
		verbose_name = _("Email Message Bcc Data")
		verbose_name_plural = _("Email Message Bcc Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageCcData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="cc")
	data = models.TextField(_("Carbon Copies"), editable=False)

	class Meta:
		verbose_name = _("Email Message Cc Data")
		verbose_name_plural = _("Email Message Cc Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EmailMessageToData(models.Model):
	email_message = models.OneToOneField(EmailMessage, primary_key=True, related_name="to")
	data = models.TextField(_("To"), editable=False)

	class Meta:
		verbose_name = _("Email Message To Data")
		verbose_name_plural = _("Email Message To Data")

	def __unicode__(self):
		return "{0}".format(self.email_message)


class EventType(models.Model):
	name = models.CharField(unique=True, max_length=EVENT_NAME_MAX_LENGTH)

	def __unicode__(self):
		return self.name


class Event(models.Model):
	email_message = models.ForeignKey(EmailMessage)
	email = models.EmailField()
	event_type = models.ForeignKey(EventType)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now=True)
	#this column should always be populated by sendgrids mandatory timestamp param
	#null=True only because this was added later and need to distinguish old columns saved before this change
	timestamp = models.DateTimeField(null=True)

	class Meta:
		verbose_name = _("Event")
		verbose_name_plural = _("Events")

	def __unicode__(self):
		return u"{0} - {1}".format(self.email_message, self.event_type)

class ClickUrl(models.Model):
	url = models.TextField()

class ClickEvent(Event):
	click_url = models.ForeignKey(ClickUrl)

	class Meta:
		verbose_name = ("Click Event")
		verbose_name_plural = ("Click Events")

	def __unicode__(self):
		return u"{0} - {1}".format(super(ClickEvent,self).__unicode__(),self.url)

	def get_url(self):
		return self.click_url.url

	def set_url(self,url):
		try:
			self.click_url = ClickUrl.objects.get_or_create(url=url)[0]
		except MultipleObjectsReturned:
			self.click_url = ClickUrl.objects.filter(url=url).order_by('id')[0]
	url = property(get_url,set_url)

class BounceReason(models.Model):
	reason = models.TextField()

class BounceType(models.Model):
	type = models.CharField(max_length=32,unique=True)

class BounceEvent(Event):
	status = models.CharField(max_length=16)
	bounce_reason = models.ForeignKey(BounceReason,null=True)
	bounce_type = models.ForeignKey(BounceType,null=True)
	class Meta:
		verbose_name = ("Bounce Event")
		verbose_name_plural = ("Bounce Events")

	def __unicode__(self):
		return u"{0} - {1}".format(super(self,BounceEvent).__unicode__(),reason)

	def get_reason(self):
		return self.bounce_reason.reason

	def set_reason(self,reason):
		self.bounce_reason = BounceReason.objects.get_or_create(reason=reason)[0]
	reason = property(get_reason,set_reason)

	def get_type(self):
		return self.bounce_type.type

	def set_type(self,reason):
		self.bounce_type = BounceType.objects.get_or_create(type=reason)[0]
	type = property(get_type,set_type)

class DeferredEvent(Event):
	response = models.TextField()
	attempt = models.IntegerField()

class DroppedEvent(Event):
	reason = models.CharField(max_length=255)

class DeliverredEvent(Event):
	response = models.TextField()
