from django.test import TestCase
from django_snooze import apis


class APITestCase(TestCase):
    def setUp(self):
        """Sets up an API object to play with.

        :returns: None

        """
        self.api = apis.api
        self.api.discover_models()

    def test_apps(self):
        """Test if the right apps are present.

        :returns: None

        """
        self.assertIn('tests', self.api._resources.keys())
        self.assertIn('auth', self.api._resources.keys())
