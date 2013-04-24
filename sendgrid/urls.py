from django.conf.urls.defaults import patterns, include, url

from .views import listener
from .views import CrossfilterReport


urlpatterns = patterns('',
	url(r"^events/$", "sendgrid.views.listener", name="sendgrid_post_event"),
	url(r"^messages/(?P<message_id>[-\w]+)/attachments/$",
		"sendgrid.views.download_attachments",
		name="sendgrid_download_attachments"
	),
)

# Reports
urlpatterns += patterns('',
	(r'^reports/$', CrossfilterReport.as_view()),
)
