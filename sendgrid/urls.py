from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

from .views import listener


urlpatterns = patterns('',
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
	url(r"^messages/(?P<email_message_id>\S+)/attachments/$",
		"sendgrid.views.download_attachments",
		name="sendgrid_download_attachments"
	),
)
