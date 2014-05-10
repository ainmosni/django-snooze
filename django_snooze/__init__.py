# -*- coding: utf-8 -*-
__version__ = '0.1.0'


def urls():
    from django_snooze.apis import api
    return api.urls


def autodiscover():
    from django_snooze.apis import api
    api.discover_models()
