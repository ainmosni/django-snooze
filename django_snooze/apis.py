# -*- coding: utf-8 -*-

from django.db.models import get_models
from django.core.urlresolvers import reverse

from django_snooze.utils import json_response
from django_snooze.resource import ModelResource


class API(object):
    """
    This is the main API class, we will use this for autodiscovery and URL
    routing.
    """

    def __init__(self, name='django_snooze', app_name='django_snooze'):
        self._resources = {}
        self.name = name
        self.app_name = app_name

    def discover_models(self):
        """
        This discovers all available models adds them to the resource registry.
        """
        for model in get_models():
            # We don't want abstract classes to become resources.
            if model._meta.abstract:
                continue
            app = model._meta.app_label
            resources = self._resources.get(app, [])
            resources.append(ModelResource(model))
            self._resources[app] = resources

    def get_urls(self):
        """
        Constructs the API urls based on what models are registered.
        """
        from django.conf.urls import url

        # Base URL patterns
        urlpatterns = [
            url(r'^$', self.index, name='index'),
        ]

        for app, resources in self._resources.items():
            for resource in resources:
                urlpatterns += [
                    url(resource.query_url_re,
                        resource.view,
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

    def index(self, request):
        """
        The root view of our API, this will return a JSON mapping of all
        available resources.
        """
        resource_str = {}
        for app, resources in self._resources.items():
            resource_str[app] = []
            for resource in resources:
                model_info = {
                    'name': resource.model_name,
                    'query_path': reverse('{}:{}'.format(
                        self.app_name,
                        resource.query_reverse_name
                    )),
                    'schema_path': reverse('{}:{}'.format(
                        self.app_name,
                        resource.schema_reverse_name
                    )),
                    'new_path': reverse('{}:{}'.format(
                        self.app_name,
                        resource.new_reverse_name
                    )),
                }
                resource_str[app].append(model_info)

        return json_response(resource_str)

# This is a default API object that we will use throughout django_snooze
api = API()
