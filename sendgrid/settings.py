from django.conf import settings

# This is experimental, use with caution.
SENDGRID_CREATE_MISSING_EMAIL_MESSAGES = getattr(settings, "SENDGRID_CREATE_MISSING_EMAIL_MESSAGES", False)
