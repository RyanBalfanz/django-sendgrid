from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url

from .views import listener
from sendgrid.views import email_message_detail
from sendgrid.views import email_message_list


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
	url(r"^messages/(?P<message_id>[-\w]+)/attachments/$",
		"sendgrid.views.download_attachments",
		name="sendgrid_download_attachments"
	),
)
