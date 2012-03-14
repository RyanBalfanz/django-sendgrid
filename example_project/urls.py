from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/sendgrid/'}, name='home'),
	url(r"^$", include("example_project.main.urls"), name="index"),
	url(r"^sendgrid/", include("sendgrid.urls")),
	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)
