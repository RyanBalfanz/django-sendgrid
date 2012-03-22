from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

# from main.views import send_simple_email

from .views import listener


urlpatterns = patterns('',
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
)
