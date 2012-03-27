from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth.models import User


SENDGRID_USER_MIXIN_ENABLED = getattr(settings, "SENDGRID_USER_MIXIN_ENABLED", True)

if SENDGRID_USER_MIXIN_ENABLED:
	from .mixins import SendGridUserMixin
	User.__bases__ += (SendGridUserMixin,)
