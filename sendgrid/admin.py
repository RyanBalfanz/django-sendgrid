from __future__ import absolute_import

from django.contrib import admin

from .models import EmailMessage
from .models import EmailMessageAttachmentsData
from .models import EmailMessageBodyData
from .models import EmailMessageBccData
from .models import EmailMessageCcData
from .models import EmailMessageExtraHeadersData
from .models import EmailMessageSubjectData
from .models import EmailMessageToData


class EmailMessageGenericDataInline(admin.TabularInline):
	model = None
	readonly_fields = ("data",)
	max_num = 1
	can_delete = False


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


class EmailMessageSubjectDataInline(EmailMessageGenericDataInline):
	model = EmailMessageSubjectData


class EmailMessageToDataInline(EmailMessageGenericDataInline):
	model = EmailMessageToData


class EmailMessageAdmin(admin.ModelAdmin):
	date_hierarchy = "creation_time"
	list_display = ("message_id", "from_email", "to_email", "subject_data", "response")
	list_filter = ("from_email", "subject__data", "response")
	readonly_fields = ("message_id", "from_email", "to_email", "response")
	inlines = (
		EmailMessageToDataInline,
		EmailMessageCcInline,
		EmailMessageBccInline,
		EmailMessageSubjectDataInline,
		EmailMessageBodyDataInline,
		EmailMessageExtraHeadersDataInline,
		EmailMessageAttachmentsDataInline,
	)


class EmailMessageGenericDataAdmin(admin.ModelAdmin):
	list_display = ("email_message", "data")


admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(EmailMessageAttachmentsData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageBccData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageBodyData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageCcData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageExtraHeadersData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageSubjectData, EmailMessageGenericDataAdmin)
admin.site.register(EmailMessageToData, EmailMessageGenericDataAdmin)
