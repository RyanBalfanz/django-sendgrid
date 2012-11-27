from django.conf import settings


SENDGRID_CREATE_MISSING_EMAIL_MESSAGES = getattr(settings, "SENDGRID_CREATE_MISSING_EMAIL_MESSAGES", False)
