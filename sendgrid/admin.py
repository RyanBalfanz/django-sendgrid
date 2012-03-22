from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import SendGridEvent
from .models import SendGridEmailMessage


class SendGridEventInline(admin.TabularInline):
	model = SendGridEvent
	can_delete = True
	extra = 0
	verbose_name = "Event"
	verbose_name_plural = "Events"


class SendGridEmailMessageAdmin(admin.ModelAdmin):
	list_display = ("message_id", "creation_time", "last_modified_time", "status", "event_count")
	# list_filter = ("status",)
	search_fields = ("message_id",)
	list_select_related = True
	
	inlines = [SendGridEventInline]
	
	fieldsets = (
		(None, {
			"fields": ("message_id",)
		}),
		(_("Text Body"), {
			"fields": ("text_body",),
			"classes": ("collapse", "closed")
		}),
		(_("HTML Body"), {
			"fields": ("html_body",),
			"classes": ("collapse", "closed")
		}),
		# (_("Advanced"), {
		# 	"fields": ("headers", "attachments"),
		# 	"classes": ("collapse", "closed")
		# })
	)


admin.site.register(SendGridEmailMessage, SendGridEmailMessageAdmin)
