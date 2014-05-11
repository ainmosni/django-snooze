from django.conf.urls import patterns, include, url

import django_snooze
django_snooze.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api/', include(django_snooze.urls())),
)
