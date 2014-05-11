# -*- coding: utf-8 -*-

from django.forms.models import modelform_factory

from django_snooze import fields
from django_snooze.views import (QueryView,
                                 SchemaView,
                                 ObjectView,
                                 NewObjectView)


class ModelResource(object):
    """
    This is the base model resource, it takes a model and will create an API
    object.
    """

    def __init__(self, model, api):
        """This inspects all the model's meta information and process it to
        extract all the information we need.

        :param model: The model to inspect.
        :param api: The API object that spawned this resource.
        :returns: None

        """
        self.model = model
        self.app = model._meta.app_label
        self.model_name = model._meta.model_name
        self.api = api

        self.queryset = self.get_queryset()
        self.form = self.get_form()

        self.fields = self.get_fields()
        self.fields_dict = self.get_fields_dict()

        self.query_view = self.get_query_view()
        self.query_url_re = self.get_query_url_re()
        self.query_reverse_name = self.get_query_reverse_name()

        self.schema_view = self.get_schema_view()
        self.schema_url_re = self.get_schema_url_re()
        self.schema_reverse_name = self.get_schema_reverse_name()

        self.pk_view = self.get_pk_view()
        self.pk_url_re = self.get_pk_url_re()
        self.pk_reverse_name = self.get_pk_reverse_name()

        self.new_view = self.get_new_view()
        self.new_url_re = self.get_new_url_re()
        self.new_reverse_name = self.get_new_reverse_name()

    def get_url_re_base(self):
        """
        Method to get the URL base regular expression.
        """
        return r'^{}/{}/'.format(self.app, self.model_name)

    def get_queryset(self):
        """Gets the queryset of the model.

        :returns: The queryset

        """
        # TODO: Change this to detect it in the meta class of the model.
        return self.model.objects.all()

    def get_form(self):
        """Gets a modelform of the current model, to be used for creation and
        editing.

        :returns: A ModelForm

        """
        return modelform_factory(self.model)

    def get_fields(self):
        """
        Gets all the fields of the model.
        """
        model_fields = [getattr(fields, x.__class__.__name__)(x)
                        for x in self.model._meta.fields]

        return model_fields

    def get_fields_dict(self):
        """Adds all fields to a dictionary, keyed by name.

        :returns: A dictionary of fields.

        """
        return {x.name: x for x in self.fields}

    def get_query_view(self):
        """Constructs the QueryView object for this resource.

        :returns: The initialised QueryView object for this resource.

        """
        return QueryView.as_view(resource=self)

    def get_query_url_re(self):
        """
        Method to get the query URL regular expression.
        """
        return self.get_url_re_base() + r'$'

    def get_query_reverse_name(self):
        """
        Method to get the name for the query URL.
        """
        return 'snooze_{}_{}_query'.format(self.app, self.model_name)

    def get_schema_view(self):
        """Constructs the SchemaView object for this resource.

        :returns: The initialised SchemaView object for this resource.

        """
        return SchemaView.as_view(resource=self)

    def get_schema_url_re(self):
        """
        Method to get the schema URL regular expression.
        """
        return self.get_url_re_base() + r'schema/$'

    def get_schema_reverse_name(self):
        """
        Method to get the name for the schema URL.
        """
        return 'snooze_{}_{}_schema'.format(self.app, self.model_name)

    def get_pk_view(self):
        """Constructs the ObjectView for this resource.

        :returns: The initialised ObjectView object for this resource.

        """
        return ObjectView.as_view(resource=self)

    def get_pk_url_re(self):
        """Constructs the primary key regular expression.

        :returns: A regular expression string.

        """
        # TODO: Detect different kinds of primary key than plain old integers.
        return self.get_url_re_base() + r'(?P<pk_url_arg>\d+)/$'

    def get_pk_reverse_name(self):
        """Generates a reverse lookup name for the pk URL.

        :returns: A reverse lookup string.

        """
        return 'snooze_{}_{}_pk'.format(self.app, self.model_name)

    def get_new_view(self):
        """Constructs the NewObjectView.

        :returns: The initialised NewObjectView.

        """
        return NewObjectView.as_view(resource=self)

    def get_new_url_re(self):
        """Constructs the regular expression for the 'new' URL.

        :returns: A regular expression string.

        """
        return self.get_url_re_base() + r'new/$'

    def get_new_reverse_name(self):
        """Generates a reverse lookup name for the new URL.

        :returns: A reverse lookup string.

        """
        return 'snooze_{}_{}_new'.format(self.app, self.model_name)

    def obj_to_json(self, obj):
        """Convert an object to a json serialisable object.

        :param obj: The object to serialise.
        :returns: A serialisable object.

        """
        obj_dict = {}
        for obj_field in self.fields:
            obj_dict[obj_field.name] = obj_field.to_json(
                getattr(obj, obj_field.name)
            )
        return obj_dict

    def __unicode__(self):
        return u'snooze resource for {}-{}'.format(self.app, self.model_name)
