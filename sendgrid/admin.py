from __future__ import absolute_import

from django.contrib import admin

from .models import SendGridEvent


class SendGridEventInline(admin.TabularInline):
	model = SendGridEvent
	can_delete = True
	extra = 0
	verbose_name = "Event"
	verbose_name_plural = "Events"


admin.site.register(SendGridEmailMessage, SendGridEmailMessageAdmin)
