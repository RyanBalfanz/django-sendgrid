from django.conf.urls.defaults import patterns, include, url

from main.views import send_simple_email

urlpatterns = patterns('',
	url(r'^$', send_simple_email),
)
