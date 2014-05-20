# -*- coding: utf-8 -*-

import json

from django.test import TestCase
from django.test.client import Client
from django.core import management
from django.utils.encoding import smart_text

from tests.models import Simple


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

    def test_fetch_nonexistent(self):
        r = self.client.get('/api/tests/simple/10/')
        self.assertEqual(404, r.status_code)

    def test_create_full(self):
        new_obj_dict = {
            u'one': 42,
            u'two': 'Eggs and spam'
        }
        r = self.client.post('/api/tests/simple/new/',
                             data=json.dumps(new_obj_dict),
                             content_type='application/json')
        self.assertEqual(201, r.status_code)
        r_data = json.loads(smart_text(r.content))
        new_obj = Simple.objects.get(pk=r_data['pk'])
        self.assertEqual(new_obj.one, new_obj_dict['one'])
        self.assertEqual(new_obj.two, new_obj_dict['two'])
        self.assertEqual(new_obj.pk, r_data['pk'])

    def test_create_partial(self):
        new_obj_dict = {
            u'one': 42,
        }
        r = self.client.post('/api/tests/simple/new/',
                             data=json.dumps(new_obj_dict),
                             content_type='application/json')
        self.assertEqual(201, r.status_code)
        r_data = json.loads(smart_text(r.content))
        new_obj = Simple.objects.get(pk=r_data['pk'])
        self.assertEqual(new_obj.one, new_obj_dict['one'])
        self.assertEqual(new_obj.two, u'spam')
        self.assertEqual(new_obj.pk, r_data['pk'])

    def test_create_incomplete(self):
        new_obj_dict = {
            u'two': 'Need more data',
        }
        r = self.client.post('/api/tests/simple/new/',
                             data=json.dumps(new_obj_dict),
                             content_type='application/json')
        self.assertEqual(400, r.status_code)

    def test_create_wrong_input(self):
        new_obj_dict = {
            u'two': 'Need more data',
        }
        r = self.client.post('/api/tests/simple/new/',
                             data=new_obj_dict)
        self.assertEqual(400, r.status_code)

    def test_query_all(self):
        r = self.client.get('/api/tests/simple/')
        self.assertEqual(200, r.status_code)
        r_data = json.loads(smart_text(r.content))
        self.assertEqual(3, len(r_data['objects']))
        self.assertEqual(111, r_data['objects'][0]['one'])
        self.assertEqual('Some string', r_data['objects'][0]['two'])

    def test_query_filtered(self):
        r = self.client.get('/api/tests/simple/?two=Some+other+string')
        self.assertEqual(200, r.status_code)
        r_data = json.loads(smart_text(r.content))
        self.assertEqual(1, len(r_data['objects']))
        self.assertEqual(222, r_data['objects'][0]['one'])
        self.assertEqual('Some other string', r_data['objects'][0]['two'])

    def test_query_excluded(self):
        r = self.client.get('/api/tests/simple/?!two=Some+other+string')
        self.assertEqual(200, r.status_code)
        r_data = json.loads(smart_text(r.content))
        self.assertEqual(2, len(r_data['objects']))
        for obj in r_data['objects']:
            self.assertNotEqual(222, obj['one'])
            self.assertNotEqual('Some other string', obj['two'])

    def test_query_combined(self):
        r = self.client.get(
            '/api/tests/simple/?two__contains=string&!two__contains=Some')
        self.assertEqual(200, r.status_code)
        r_data = json.loads(smart_text(r.content))
        self.assertEqual(1, len(r_data['objects']))
        self.assertEqual(333, r_data['objects'][0]['one'])
        self.assertEqual('Yet another string', r_data['objects'][0]['two'])

    def test_query_in(self):
        r = self.client.get('/api/tests/simple/?one__in=111&one__in=333')
        self.assertEqual(200, r.status_code)
        r_data = json.loads(smart_text(r.content))
        self.assertEqual(2, len(r_data['objects']))
        for obj in r_data['objects']:
            self.assertNotEqual(222, obj['one'])
            self.assertNotEqual('Some other string', obj['two'])

    def test_query_invalid_field(self):
        r = self.client.get('/api/tests/simple/?three=333')
        self.assertEqual(400, r.status_code)

    def test_query_invalid_lookup(self):
        r = self.client.get('/api/tests/simple/?two__may=Some+other+string')
        self.assertEqual(400, r.status_code)
