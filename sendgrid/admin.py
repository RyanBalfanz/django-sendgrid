from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import SendGridEvent
from .models import SendGridEmailMessage


class SendGridEventInline(admin.TabularInline):
	model = SendGridEvent
	can_delete = False
	
	max_num = 1
	extra = 0
	
	readonly_fields = ("id",)


class SendGridEmailMessageAdmin(admin.ModelAdmin):
	# list_display = ("to", "to_type", "subject", "tag", "status", "submitted_at")
	# list_filter = ("status", "tag", "to_type", "submitted_at")
	# search_fields = ("message_id", "to", "subject")
	list_select_related = True
	
	# readonly_fields = ("message_id", "status", "subject", "tag", "to", "to_type", "sender", "reply_to", "submitted_at", "text_body", "html_body", "headers", "attachments")
	
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


# class SendGridEventAdmin(admin.ModelAdmin):
# 	pass

admin.site.register(SendGridEmailMessage, SendGridEmailMessageAdmin)
admin.site.register(SendGridEvent)
