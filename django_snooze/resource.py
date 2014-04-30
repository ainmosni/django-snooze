# -*- coding: utf-8 -*-

from collections import OrderedDict
from django_snooze.utils import json_response
from django_snooze.fields import field


class ModelResource(object):
    """
    This is the base model resource, it takes a model and will create an API
    object.
    """

    def __init__(self, model):
        """
        This inspects all the model's meta information and process it to
        extract all the information we need.

        Arguments:
            - model (required): The model to inspect.
        """
        self.model = model
        self.app = model._meta.app_label
        self.model_name = model._meta.model_name
        self.query_url_re = self.get_query_url_re()
        self.schema_re = self.get_schema_url_re()
        self.query_reverse_name = self.get_query_reverse_name()
        self.schema_reverse_name = self.get_schema_reverse_name()
        self.fields = self.get_fields()
        self.queryset = self.get_queryset()

    def get_url_re_base(self):
        """
        Method to get the URL base regular expression.
        """
        return r'^{}/{}/'.format(self.app, self.model_name)

    def get_query_url_re(self):
        """
        Method to get the query URL regular expression.
        """
        return self.get_url_re_base() + r'$'

    def get_schema_url_re(self):
        """
        Method to get the schema URL regular expression.
        """
        return self.get_url_re_base() + r'schema/$'

    def get_query_reverse_name(self):
        """
        Method to get the name for the query URL.
        """
        return '{}-{}'.format(self.app, self.model_name)

    def get_schema_reverse_name(self):
        """
        Method to get the name for the schema URL.
        """
        return '{}-{}-schema'.format(self.app, self.model_name)

    def get_fields(self):
        """
        Gets all the fields of the model.
        """
        fields = [getattr(field, x.__class__.__name__)(x)
                  for x in self.model._meta.fields]

        return fields

    def get_queryset(self):
        """Gets the queryset of the model.

        :returns: The queryset

        """
        # TODO: Change this to detect it in the meta class of the model.
        return self.model.objects.all()

    def view(self, request):
        """
        View handler.
        """
        # Set self.request so that we don't have to pass it around all the time
        self.request = request
        if request.method == 'GET':
            content = self.get()
        elif request.method == 'POST':
            content = self.post()
        else:
            return json_response({'error': 'Bad request'}, status_code=400)
        return json_response(content)

    def get(self):
        """Handle a GET request.

        :returns: A json serialisable object.

        """
        content = {}
        objects = []

        # TODO: Make this faster?
        for obj in self.queryset:
            obj_dict = {}
            for obj_field in self.fields:
                obj_dict[obj_field.name] = obj_field.to_json(
                    getattr(obj, obj_field.name)
                )
            objects.append(obj_dict)

        content['objects'] = objects
        return content

    def schema_view(self, request):
        """
        Schema handler.
        """
        schema = OrderedDict()
        for f in self.fields:
            schema[f.name] = f.schema_info()
        return json_response(schema)

    def __unicode__(self):
        return '{}-{}'.format(self.app, self.model_name)
