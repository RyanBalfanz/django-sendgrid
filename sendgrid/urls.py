from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

from .views import listener


urlpatterns = patterns('',
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
	url(r"^messages/(?P<email_message_id>\S+)/attachements/$",
		"sendgrid.views.download_attachment",
		name="sendgrid_download_attachment"
	),
)
