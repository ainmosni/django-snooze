# -*- coding: utf-8 -*-

from django.db.models import get_models

from django_snooze.resource import ModelResource
from django_snooze.views import IndexView


class API(object):
    """
    This is the main API class, we will use this for autodiscovery and URL
    routing.
    """

    def __init__(self, name='django_snooze', app_name='django_snooze'):
        self._resources = {}
        self.name = name
        self.app_name = app_name
        self.index_view = self.get_index_view()
        self.discovered = False

    def discover_models(self):
        """
        This discovers all available models adds them to the resource registry.
        """
        # We only want this to run once.
        if self.discovered:
            return True

        for model in get_models():
            app = model._meta.app_label
            resources = self._resources.get(app, [])
            resources.append(ModelResource(model, self))
            self._resources[app] = resources
        self.discovered = True
        return True

    def get_index_view(self):
        """Constructs an initialised IndexView.

        :returns: An initialised IndexView

        """
        return IndexView.as_view(api=self)

    def get_urls(self):
        """
        Constructs the API urls based on what models are registered.
        """
        from django.conf.urls import url

        # Base URL patterns
        urlpatterns = [
            url(r'^$', self.index_view, name='index'),
        ]

        for app, resources in self._resources.items():
            for resource in resources:
                urlpatterns += [
                    url(resource.query_url_re,
                        resource.query_view,
                        name=resource.query_reverse_name),
                    url(resource.schema_url_re,
                        resource.schema_view,
                        name=resource.schema_reverse_name),
                    url(resource.pk_url_re,
                        resource.pk_view,
                        name=resource.pk_reverse_name),
                    url(resource.new_url_re,
                        resource.new_view,
                        name=resource.new_reverse_name),
                ]

        return urlpatterns

    @property
    def urls(self):
        return (self.get_urls(), self.app_name, self.name)

# This is a default API object that we will use throughout django_snooze
api = API()
