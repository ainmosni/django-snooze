from django.test import TestCase
from django.core import management

from django_snooze import apis
from django_snooze.resource import ModelResource
from django_snooze.fields import IntegerField, CharField

from tests.models import Simple


class ResourceTestCase(TestCase):

    def setUp(self):
        self.api = apis.api
        self.api.discover_models()
        self.resource = ModelResource(Simple, self.api)
        management.call_command('loaddata',
                                'django_snooze/fixtures/test_data.json',
                                verbosity=0)

    def tearDown(self):
        management.call_command('flush', interactive=False, verbosity=0)

    def test_class_variables(self):
        self.assertEqual(u'tests', self.resource.app)
        self.assertEqual(u'simple', self.resource.model_name)
        self.assertIs(Simple, self.resource.model)

    def test_dynamic_variables(self):
        self.assertEqual(set(Simple.objects.all()),
                         set(self.resource.queryset))

    def test_fields(self):
        self.assertEqual(3, len(self.resource.fields))
        self.assertIn('one', self.resource.fields_dict.keys())
        self.assertIn('two', self.resource.fields_dict.keys())
        self.assertIsInstance(self.resource.fields_dict['one'], IntegerField)
        self.assertIsInstance(self.resource.fields_dict['two'], CharField)

    def test_json_serialisation(self):
        obj = Simple.objects.get(pk=1)
        obj_dict = self.resource.obj_to_json(obj)
        self.assertIn('id', obj_dict)
        self.assertIn('one', obj_dict)
        self.assertIn('two', obj_dict)
        self.assertEqual(1, obj_dict['id'])
        self.assertEqual(111, obj_dict['one'])
        self.assertEqual('Some string', obj_dict['two'])

    def test_stringify(self):
        self.assertEqual(u'snooze resource for tests-simple',
                         self.resource.__unicode__())
