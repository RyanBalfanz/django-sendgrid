import datetime
import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

# django-sendgrid
import constants
from sendgrid.models import EmailTemplate as Email
from sendgrid.message import SendGridEmailMessage
from sendgrid.signals import sendgrid_email_sent

logger = logging.getLogger(__name__)


class SendGridEvent(models.Model):
	"""
	A SendGrid Event.
	"""
	EMAIL_EVENT_UNKNOWN = constants.EMAIL_EVENT_UNKNOWN
	EMAIL_EVENT_PROCESSED = constants.EMAIL_EVENT_PROCESSED
	EMAIL_EVENT_DROPPED = constants.EMAIL_EVENT_DROPPED
	EMAIL_EVENT_DEFERRED = constants.EMAIL_EVENT_DEFERRED
	EMAIL_EVENT_DELIVERED = constants.EMAIL_EVENT_DEFERRED
	EMAIL_EVENT_BOUNCED = constants.EMAIL_EVENT_BOUNCED
	EMAIL_EVENT_CLICKED = constants.EMAIL_EVENT_CLICKED
	EMAIL_EVENT_OPENED = constants.EMAIL_EVENT_OPENED
	EMAIL_EVENT_UNSUBSCRIBED = constants.EMAIL_EVENT_UNSUBSCRIBED
	EMAIL_EVENT_SPAM = constants.EMAIL_EVENT_SPAM
	EMAIL_EVENT_TYPES = (
		(EMAIL_EVENT_UNKNOWN, _("Unknown")),
		(EMAIL_EVENT_PROCESSED, _("Processed")),
		(EMAIL_EVENT_DROPPED, _("Dropped")),
		(EMAIL_EVENT_DEFERRED, _("Deferred")),
		(EMAIL_EVENT_DELIVERED, _("Delivered")),
		(EMAIL_EVENT_BOUNCED, _("Bounced")),
		(EMAIL_EVENT_CLICKED, _("Clicked")),
		(EMAIL_EVENT_OPENED, _("Opened")),
		(EMAIL_EVENT_UNSUBSCRIBED, _("Unsubscribed")),
	)
	
	short_description = models.CharField(_("Short Description"), blank=True, max_length=constants.EVENT_SHORT_DESC_MAX_LENGTH)
	long_description = models.TextField(_("Long Description"), blank=True)
	type = models.IntegerField(_("Type"), choices=EMAIL_EVENT_TYPES, default=EMAIL_EVENT_UNKNOWN)


	class Admin:
		list_display = ("short_description", "type")
		search_fields = ("",)
		filter_fields = ("type")

	def __unicode__(self):
		return u"SendGridEvent {type}".format(type=self.type)


class SendGridTrackedEmail(models.Model):
	"""(SendGridTrackedEmail description)"""
	email = models.ForeignKey(Email)
	creation_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	recipient = models.CharField(blank=True, max_length=100)
	# recipient_list = models.TextField(blank=True)
	# recipients = models.PickledField(blank=True)
	subject = models.CharField(blank=True, max_length=100)
	message = models.TextField(blank=True)
	events = models.ManyToManyField(SendGridEvent, through="SendGridEmailEvent")
	

	class Admin:
		list_display = ('',)
		search_fields = ('',)

	def __unicode__(self):
		return u"SendGridTrackedEmail {email}".format(email=self.email)
		
	def save(self, *args, **kwargs):
		"""
		Saves the object.
		"""
		self.last_modified_time = datetime.datetime.now()
		super(SendGridTrackedEmail, self).save(*args, **kwargs)
		
	def get_ordered_events(self, ordering="asc", limit=None, offset=None):
		"""
		Gets all events in order.
		"""
		if ordering.lower() == "asc":
			orderBy = "creation_time"
		elif ordering.lower() == "desc":
			orderBy = "-creation_time"
		else:
			message = "ordering {o} is invalid".format(o=ordering)
			logger.info(message)
			# raise ValueError(message)
			
		return self.events().all().order_by(orderBy)
		
	def is_unknown(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_UNKNOWN`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_UNKNOWN).exists()
	unknown = property(is_unknown)
	
	def was_processed(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_PROCESSED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_PROCESSED).exists()
	processed = property(was_processed)
	
	def was_dropped(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_DROPED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_DROPED).exists()
	dropped = property(was_dropped)
	
	def was_deferred(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_DEFERRED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_DEFERRED).exists()
	deferred = property(was_deferred)
	
	def was_delivered(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_DELIVERED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_DELIVERED).exists()
	delivered = property(was_delivered)
	
	def was_bounced(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_BOUNCED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_BOUNCED).exists()
	bounced = property(was_bounced)
	
	def was_clicked(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_CLICKED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_CLICKED).exists()
	clicked = property(was_clicked)
	
	def was_opened(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_OPENED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_OPENED).exists()
	opened = property(was_opened)
	
	def was_unsubscribed(self):
		"""
		Returns True if any events of type ``EMAIL_EVENT_UNSUBSCRIBED`` exist.
		"""
		return self.events.filter(type=SendGridEvent.EMAIL_EVENT_UNSUBSCRIBED).exists()
	unsubscribed = property(was_unsubscribed)


class SendGridEmailEvent(models.Model):
	"""docstring for SendGridEmailEvent"""
	email = models.ForeignKey(SendGridTrackedEmail)
	event = models.ForeignKey(SendGridEvent)
	creation_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	last_modified_time = models.DateTimeField(blank=True, default=datetime.datetime.now)
	
	class Admin:
		list_display = ("short_description", "type")
		search_fields = ("",)
		filter_fields = ("type")

	def __unicode__(self):
		return u"SendGridEvent {type}".format(type=self.type)
		
	def save(self, *args, **kwargs):
		"""docstring for save"""
		last_modified_time = datetime.datetime.now()
		super(SendGridEmailEvent, self).save(*args, **kwargs)


# @receiver(sendgrid_email_sent)
# def create_event(sender, instance, *args, **kwargs):
# 	"""docstring for create_event"""
# 	logger.debug("sendgrid_email_sent signal recieved for {i}".format(i=instance))
# 	
# 	instance_id = instance.name
# 	instance_subject = instance.subject
# 	instance_message = instance.message
# 		
# 	trackedEmail = SendGridTrackedEmail.objects.create(
# 		email=instance_id,
# 		subject=instance_subject,
# 		message=instance_subject,
# 	)
# 	
# 	return
	
@receiver(post_save, sender=SendGridTrackedEmail)
def log_tracked_email_created(sender, instance, *args, **kwargs):
	"""
	Logs a message when a ``SendGridTrackedEmail`` is created.
	"""
	if created:
		message = "SendGridTrackedEmail created: {i}"
		logger.debug(message.format(i=instance))
	
	return
	