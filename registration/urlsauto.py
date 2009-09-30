from django.conf.urls.defaults import patterns, include

rootpatterns = patterns('',
    (r'^account/', include('registration.urls')),
)
