# -*- coding: utf-8 -*-

import simplejson as json
from flask.views import MethodView
from flask.wrappers import Request, Response
from werkzeug.exceptions import HTTPException

from .. import backend

class ApiMeta(type):
    """ Metaclass used to create an API registry"""

    def __init__(cls, name, bases, dct):
        if not hasattr(cls, "registry"):
            cls.registry = {}
        else:
            interface_id = name.lower()
            cls.registry[interface_id] = cls

        super.__init__(name, bases, dict)

class Api(MethodView):
    """ Base class for API endpoints

    There are 2 ways of using this class.

    1. Define the class variables endpoint, prefix, pk["name"/"type"]
    Using this method will create a resource with the following properties:
        - it will be available at api/version/prefix/
        - it will accept the HTTP methods GET and POST
        for the api/version/prefix/ URL
        - it will accept the HTTP methods GET, PUT, POST, DELETE and PATCH
        for the api/version/prefix/primary_key_type (the primary key type
        is defined by the pk["type"] entry
    2. If you choose not to use the above method, you must redefine the
    register_api_endpoint class method. Doing so will allow you to register
    a custom endpoint.
    """

    def __init__(self):
        """ Create a new endpoint request

        Every request creates a database object
        """
        self.db = backend.get_db()

    @classmethod
    def register_api_endpoint(cls, app):
        """ Register an endpoint to the flask application """
        func = cls.as_view(cls.endpoint)
        app.add_url_rule("%s/" % cls.prefix, defaults={ cls.pk["name"]: None },
                view_func = func, methods=["GET"])
        app.add_url_rule("%s/" % cls.prefix,
                view_func = func, methods=["POST"])
        app.add_url_rule("%s/<%s:%s>" % (cls.prefix, cls.pk["type"], cls.pk["name"]),
                view_func = func, methods=["GET", "DELETE", "PATCH"])

    @classmethod
    def get_endpoints(cls):
        """ Returns all the registered endpoints """
        return cls.registry

class ApiRequest(Request):
    def on_json_loading_failed(self, e):
        from .exceptions import BadRequest
        raise BadRequest('invalid json in request')

class ApiResponse(Response):
    default_mimetype = 'application/json'
    default_error_code = 0

    def __init__(self, content, status=None, error_code=None):
        if error_code is None:
            error_code = self.default_error_code
        if status is None:
            status = self.default_status

        Response.__init__(self, response=json.dumps({
            'result': content,
            'errorCode': error_code
            }), status=status)

class ApiException(HTTPException):
    error_code = None

    def get_response(self, environ=None):
        return ApiResponse(self.description,
            status=self.code, error_code=self.error_code)
