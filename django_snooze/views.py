"""
This will contain all the generic CBVs to handle all requests.
"""
import json
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text


class RESTView(View):
    """
    Generic REST view, will respond with a serialised response.

    It keeps the api and resource variable to get access to their variables.
    """

    def render_serialised_response(self, content, status_code=200, **kwargs):
        """Figure out what serialiser we need and delegate to the right one.
        Only JSON is supported for now.

        :param content: The content to serialise.
        :param status_code: The status code of the response.
        :param **kwargs: Additional content to be set.
        :returns: HttpResponse with the right content.
        """
        response = HttpResponse()
        response.status_code = status_code
        for k, v in kwargs.items():
            response[k] = v
        # TODO: Do some actal delegating here. This is setup for now so that
        # will be easier later.
        (serialised_content, content_type) = self._serialise_to_json(content)
        response.write(serialised_content)
        response['Content-Type'] = content_type
        return response

    def _serialise_to_json(self, content):
        """Serialises content to json.

        :param content: The content to serialise.
        :returns: A tuple of the serialised content and the content-type.

        """
        serialised_content = json.dumps(content)
        content_type = 'application/json; charset=utf-8'
        return (serialised_content, content_type)

    def get(self, request, *args, **kwargs):
        """Handles get requests.

        :param request: The django request object.
        :param *args: Optional argumenta.
        :param **kwargs: Optional keyword arguments.
        :returns: The response.

        """
        # XXX: Use exceptions for cleaner error-code handling?
        content, status_code = self.get_content_data(**kwargs)
        return self.render_serialised_response(content,
                                               status_code=status_code)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Overriden dispatch to disable CSRF on all snooze views.

        :param *args: Arguments list
        :param **kwargs: Keyword argument dict.
        :returns: The response.

        """
        return super(RESTView, self).dispatch(*args, **kwargs)


class IndexView(RESTView):
    """
    A simple CBV for showing the index of all resources.
    """

    api = None

    def get_content_data(self, **kwargs):
        """This will iterate over all apps and models discovered by the API
        and return an index data structure.

        :param **kwargs: Not used, kept because it gets passed to us.
        :returns: A tuple containing the index structure and the status code.

        """
        index_struct = {}
        for app, resources in self.api._resources.items():
            app_dict = index_struct.get(app, {})
            for resource in resources:
                app_dict[resource.model_name] = {
                    'query_path': reverse('{}:{}'.format(
                        self.api.app_name,
                        resource.query_reverse_name
                    )),
                    'schema_path': reverse('{}:{}'.format(
                        self.api.app_name,
                        resource.schema_reverse_name
                    )),
                    'new_path': reverse('{}:{}'.format(
                        self.api.app_name,
                        resource.new_reverse_name
                    ))
                }
            index_struct[app] = app_dict

        return (index_struct, 200)


class ResourceView(RESTView):
    """
    Parent class for all resource views.

    This will only contain the resource class variable for now but it's
    seperated out for possible extension reasons.
    """
    resource = None


class QueryView(ResourceView):
    """
    This view will handle queries for self.resource, it only supports GET
    requests at the moment with POST-queries planned in the near future.
    """

    http_method_names = ['get', 'head']

    def get(self, request, *args, **kwargs):
        """Overriding the get method to add a parse_get_data.

        :param request: The django request object.
        :param *args: Optional argumenta.
        :param **kwargs: Optional keyword arguments.
        :returns: The response.

        """
        self.parse_get_data(request.GET)
        return super(QueryView, self).get(request, *args, **kwargs)

    def parse_get_data(self, get_dict):
        """Parses the get parameters and sorts them for further use.

        :param get_dict: the GET dictionary
        :returns: None

        """
        # TODO: Make these configurable
        SYSTEM_PREFIX = '__'
        EXCLUDE_PREFIX = '!'

        self.system_params = {}
        self.filter_params = {}
        self.exclude_params = {}

        for key, value in get_dict.items():
            if key.startswith(SYSTEM_PREFIX):
                self.system_params[key[len(SYSTEM_PREFIX):]] = value
            elif key.startswith(EXCLUDE_PREFIX):
                self.exclude_params[key[len(EXCLUDE_PREFIX):]] = value
            else:
                self.filter_params[key] = value

    def construct_queryset(self):
        """Constructs the queryset, processes all the parameters and returns a
        queryset that conforms to the query parameters, the negation parameters
        and the system parameters.

        :returns: A fully constructed queryset.

        """
        queryset = self.resource.queryset
        queryset = self.filter_queryset(queryset)
        queryset = self.exclude_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        """Applies all the filter parameters to the queryset.

        :param queryset: The queryset to apply the filters to.
        :returns: A queryset with filters applied to it.

        """
        # TODO: Handle relations and non-existent fields.
        for query_filter, query_param in self.filter_params.items():
            queryset = queryset.filter(**{query_filter: query_param})
        return queryset

    def exclude_queryset(self, queryset):
        """Applies all the exclusion parameters to the queryset.

        :param queryset: The queryset to apply the exclusions to.
        :returns: A queryset with exclusions applied to it.

        """
        # TODO: Handle relations and non-existent fields.
        for query_filter, query_param in self.exclude_params.items():
            queryset = queryset.exclude(**{query_filter: query_param})
        return queryset

    def get_content_data(self, **kwargs):
        """Handles getting the content for the current query.

        :param **kwargs: Not used in this request.
        :returns: A tuple of the content dictionary and the status code.

        """
        content = {}
        objects = []

        # TODO: Make this faster?
        for obj in self.construct_queryset():
            obj_dict = self.resource.obj_to_json(obj)
            objects.append(obj_dict)

        content['objects'] = objects
        return (content, 200)


class SchemaView(ResourceView):
    """
    This view will handle schema requests for self.resource, it only supports
    GET requests.
    """

    http_method_names = ['get', 'head']

    def get_content_data(self, **kwargs):
        """Handles getting the schema dictionary for the current resource.

        :param **kwargs: Not used in this request.
        :returns: A tuple of the content dictionary and the status code.

        """
        schema = OrderedDict()
        for f in self.resource.fields:
            schema[f.name] = f.schema_info()
        return (schema, 200)


class ObjectView(ResourceView):
    """
    Shows the requested object.
    """

    http_method_names = ['get', 'head']

    def get_content_data(self, pk_url_arg,  **kwargs):
        """Gets a single object and returns a serialisable dictionary.

        :param pk_url_arg: The primary key of the requested object.
        :param **kwargs: Not used in this request.
        :returns: A tuple with the object dictionary and the status code.

        """
        obj = get_object_or_404(self.resource.queryset, pk=pk_url_arg)
        return (self.resource.obj_to_json(obj), 200)


class NewObjectView(ResourceView):
    """
    Creates a new object via a modelform.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """Creates an object, using the json in the request body as data of the
        modelform in the API object

        :param request: The django request object.
        :param *args: Optional arguments.
        :param **kwargs: Optional keyword arguments.
        :returns: An HttpResponse with the status of the operation.

        """
        # Assume a bad request by default.
        response = {'Status': 'Wrong Content-Type.'}
        status_code = 400

        if self.request.META.get(
            'CONTENT_TYPE', ''
        ).startswith('application/json'):
            data = json.loads(smart_text(request.body))
            # Load missing defaults if needed.
            for key, value in self.resource.field_defaults.items():
                if key not in data.keys():
                    data[key] = value
            form = self.resource.form(data=data)
            if form.is_valid():
                obj = form.save()
                response = {'Status': 'success',
                            'Location': reverse('{}:{}'.format(
                                self.resource.api.name,
                                self.resource.pk_reverse_name
                            ), args=[obj.pk]),
                            'pk': obj.pk}
                status_code = 201
            else:
                response = {'Status': 'failed',
                            'errors': form.errors}

        return self.render_serialised_response(response,
                                               status_code=status_code)
