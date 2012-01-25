from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

# django-sendgrid
from models import SendGridTrackedEmail


class SendGridTrackedEmailAdmin(admin.ModelAdmin):
	pass


admin.site.register(SendGridTrackedEmail, SendGridTrackedEmailAdmin)
