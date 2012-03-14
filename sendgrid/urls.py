from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

from main.views import send_simple_email

# django-sendgrid
# from .constants import POST_EVENT_URL as _POST_EVENT_URL
from .views import listener


# POST_EVENT_URL = getattr(settings, "POST_EVENT_URL", _POST_EVENT_URL)
# POST_EVENT_URL_PATTERN = r"^{url}$".format(url=POST_EVENT_URL)

urlpatterns = patterns('',
	# url(POST_EVENT_URL_PATTERN, post_event, name="sendgrid_post_event"),
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
)
