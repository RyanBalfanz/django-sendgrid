from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin

from .models import Argument
from .models import Category
from .models import EmailMessage
from .models import EmailMessageAttachmentsData
from .models import EmailMessageBodyData
from .models import EmailMessageBccData
from .models import EmailMessageCcData
from .models import EmailMessageExtraHeadersData
from .models import EmailMessageSendGridHeadersData
from .models import EmailMessageSubjectData
from .models import EmailMessageToData
from .models import Event
from .models import UniqueArgument


DEBUG_SHOW_DATA_ADMIN_MODELS = settings.DEBUG


class CategoryAdmin(admin.ModelAdmin):
	date_hierarchy = "creation_time"
	list_display = ("name", "creation_time", "last_modified_time", "email_message_count")
	readonly_fields = ("name", "email_message_count")
	search_fields = ("name",)

	def has_add_permission(self, request):
		return False

	def email_message_count(self, category):
		return category.emailmessage_set.count()

class EmailMessageGenericDataInline(admin.TabularInline):
	model = None
	readonly_fields = ("data",)
	max_num = 1
	can_delete = False

	def has_add_permission(self, request):
		return False


class EmailMessageAttachmentsDataInline(EmailMessageGenericDataInline):
	model = EmailMessageAttachmentsData


class EmailMessageBccInline(EmailMessageGenericDataInline):
	model = EmailMessageBccData


class EmailMessageBodyDataInline(EmailMessageGenericDataInline):
	model = EmailMessageBodyData


class EmailMessageCcInline(EmailMessageGenericDataInline):
	model = EmailMessageCcData


class EmailMessageExtraHeadersDataInline(EmailMessageGenericDataInline):
	model = EmailMessageExtraHeadersData


class EmailMessageSendGridDataInline(EmailMessageGenericDataInline):
	model = EmailMessageSendGridHeadersData


class EmailMessageSubjectDataInline(EmailMessageGenericDataInline):
	model = EmailMessageSubjectData


class EmailMessageToDataInline(EmailMessageGenericDataInline):
	model = EmailMessageToData


class EventInline(admin.TabularInline):
	model = Event
	can_delete = False
	extra = 0
	verbose_name = "Event"
	verbose_name_plural = "Events"


class UniqueArgumentsInLine(admin.TabularInline):
	model = UniqueArgument
	readonly_fields = ("data", "value",)
	extra = 0
	can_delete = False

	def has_add_permission(self, request):
		return False


class EmailMessageAdmin(admin.ModelAdmin):
	date_hierarchy = "creation_time"
	list_display = (
		"message_id",
		"from_email",
		"to_email",
		"category",
		"subject_data",
		"response",
		"creation_time",
		"last_modified_time",
		"event_count",
		"first_event_type",
		"latest_event_type",
	)
	list_display = (
		"message_id",
		"from_email",
		"to_email",
		"category",
		"subject_data",
		"response",
		"unique_argument_count"
	)
	list_filter = ("from_email", "subject__data", "category", "response")
	readonly_fields = ("message_id", "from_email", "to_email", "category", "response", "categories", "arguments", "unique_argument_count")
	inlines = (
		EmailMessageToDataInline,
		EmailMessageCcInline,
		EmailMessageBccInline,
		EmailMessageSubjectDataInline,
		EmailMessageBodyDataInline,
		EmailMessageSendGridDataInline,
		EmailMessageExtraHeadersDataInline,
		EmailMessageAttachmentsDataInline,
		EventInline,
		UniqueArgumentsInLine,
	)

	def has_add_permission(self, request):
		return False

	def first_event_type(self, emailMessage):
		return emailMessage.first_event.type

	def unique_argument_count(self, emailMessage):
		return emailMessage.uniqueargument_set.count()


class EventAdmin(admin.ModelAdmin):
	date_hierarchy = "creation_time"
	list_display = (
		"email_message",
		"type",
		"email",
		"creation_time",
		"last_modified_time",
	)
	list_filter = ("type",)
	search_fields = ("email_message__message_id",)
	readonly_fields = (
		"email_message",
		"type",
		"email",
		"creation_time",
		"last_modified_time",
	)

	def has_add_permission(self, request):
		return False


class EmailMessageGenericDataAdmin(admin.ModelAdmin):
	list_display = ("email_message", "data")


	def has_add_permission(self, request):
		return False

admin.site.register(Argument)
admin.site.register(UniqueArgument)
admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Category, CategoryAdmin)

if DEBUG_SHOW_DATA_ADMIN_MODELS:
	admin.site.register(EmailMessageAttachmentsData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageBccData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageBodyData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageCcData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageSendGridHeadersData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageExtraHeadersData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageSubjectData, EmailMessageGenericDataAdmin)
	admin.site.register(EmailMessageToData, EmailMessageGenericDataAdmin)
