"""
This will contain all the generic CBVs to handle all requests.
"""
import json
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import HttpResponse


class RESTView(View):
    """
    Generic REST view, will respond with a serialised response.

    It keeps the api and resource variable to get access to their variables.
    """

    resource = None

    def render_json_response(self, content, status_code=200, **kwargs):
        """Serialises content to the content to a response object.

        :param content: The content to serialise.
        :param status_code: The status code of the response.
        :param **kwargs: Additional headers to be set.
        :returns: HttpResponse with json content.

        """
        response = HttpResponse()
        response.write(json.dumps(content))
        response.status_code = status_code
        for k, v in kwargs.items():
            response[k] = v
        return response

    def get(self, request, *args, **kwargs):
        """Handles get requests.

        :param request: The django request object.
        :param *args: Optional argumenta.
        :param **kwargs: Optional keyword arguments.
        :returns: The response.

        """
        # TODO: Use exceptions for cleaner error-code handling?
        content, status_code = self.get_content_data(**kwargs)
        return self.render_json_response(content, status_code=status_code)


class QueryView(RESTView):
    """
    This view will handle queries for self.resource, it only supports GET
    requests at the moment with POST-queries planned in the near future.
    """

    def get_content_data(self, **kwargs):
        """Handles getting the content for the current query.

        :param **kwargs: Not used in this request.
        :returns: A tuple of the content dictionary and the status code.

        """
        content = {}
        objects = []

        # TODO: Make this faster?
        for obj in self.resource.queryset:
            obj_dict = self.resource.obj_to_json(obj)
            objects.append(obj_dict)

        content['objects'] = objects
        return (content, 200)


class SchemaView(RESTView):
    """
    This view will handle schema requests for self.resource, it only supports
    GET requests.
    """

    def get_content_data(self, **kwargs):
        """Handles getting the schema dictionary for the current resource.

        :param **kwargs: Not used in this request.
        :returns: A tuple of the content dictionary and the status code.

        """
        schema = OrderedDict()
        for f in self.resource.fields:
            schema[f.name] = f.schema_info()
        return (schema, 200)


class ObjectView(RESTView):
    """
    Shows the requested object.
    """

    def get_content_data(self, pk_url_arg,  **kwargs):
        """Gets a single object and returns a serialisable dictionary.

        :param pk_url_arg: The primary key of the requested object.
        :param **kwargs: Not used in this request.
        :returns: A tuple with the object dictionary and the status code.

        """
        obj = get_object_or_404(self.resource.queryset, pk=pk_url_arg)
        return (self.resource.obj_to_json(obj), 200)
