# -*- coding: utf-8 -*-

import json

from django.test import TestCase
from django.test.client import Client
from django.core import management
from django.utils.encoding import smart_text


class RESTTestCase(TestCase):

    def setUp(self):
        management.call_command('loaddata',
                                'django_snooze/fixtures/test_data.json',
                                verbosity=0)
        self.client = Client()

    def tearDown(self):
        management.call_command('flush', interactive=False, verbosity=0)

    def test_index(self):
        r = self.client.get('/api/')
        self.assertEqual(200, r.status_code)
        self.assertEqual(u'application/json; charset=utf-8',
                         r['Content-Type'])
        index = json.loads(smart_text(r.content))
        self.assertIn(u'tests', index)
        self.assertIn(u'simple', index['tests'])
        required_paths = set(['new_path', 'schema_path', 'query_path'])
        paths = set(index['tests']['simple'].keys())
        self.assertEqual(required_paths, paths)
        br = self.client.post('/api/', {'foo': 'bar'})
        self.assertEqual(405, br.status_code)

    def test_schema(self):
        r = self.client.get('/api/tests/simple/schema/')
        self.assertEqual(200, r.status_code)
        self.assertEqual(u'application/json; charset=utf-8',
                         r['Content-Type'])
        schema = json.loads(smart_text(r.content))
        fields = set(['id', 'one', 'two'])
        self.assertEqual(fields, set(schema.keys()))
        one = {
            u'name': u'one',
            u'type': u'IntegerField',
            u'null': False,
            u'blank': False,
            u'editable': True,
            u'help_text': u'',
            u'primary_key': False,
            u'unique': False,
        }
        self.assertEqual(one, schema['one'])
        self.assertEqual(u'spam', schema['two']['default'])

    def test_fetch(self):
        r = self.client.get('/api/tests/simple/1/')
        self.assertEqual(200, r.status_code)
        self.assertEqual(u'application/json; charset=utf-8',
                         r['Content-Type'])
        obj = json.loads(smart_text(r.content))
        x = {
            u'id': 1,
            u'one': 111,
            u'two': 'Some string',
        }
        self.assertEqual(x, obj)
