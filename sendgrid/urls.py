from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

from sendgrid.views import email_message_detail
from sendgrid.views import email_message_list
from sendgrid.views import email_message_preview


urlpatterns = patterns("",
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
	url(r"^messages/$",
		email_message_list,
		name="sendgrid_email_message_list"
	),
	url(r"^messages/(?P<slug>[-\w]+)/$",
		email_message_detail,
		name="sendgrid_email_message_detail"
	),
	url(r"^messages/(?P<slug>[-\w]+)/preview/$",
		email_message_preview,
		name="sendgrid_email_message_preview"
	),
	url(r"^messages/(?P<message_id>[-\w]+)/attachments/$",
		"sendgrid.views.download_attachments",
		name="sendgrid_download_attachments"
	),
)
