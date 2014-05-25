from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '', url(
        r'^calendar/', include('happenings.urls', namespace='calendar')
    ), url(
        r'^admin/', include(admin.site.urls)
    ),
)

urlpatterns += staticfiles_urlpatterns()
