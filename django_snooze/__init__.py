# -*- coding: utf-8 -*-

from django_snooze.apis import api

def autodiscover():
    api.discover_models()
