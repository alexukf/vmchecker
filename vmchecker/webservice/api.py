from .. import backend
from flask.views import MethodView
from flask.wrappers import Request
from werkzeug.exceptions import BadRequest

class ApiMeta(type):
    """ Metaclass used as to create an API registry"""

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
                view_func = func, methods=["GET", "PUT", "DELETE", "PATCH"])

    @classmethod
    def get_endpoints(cls):
        """ Returns all the registered endpoints """
        return cls.registry

class ApiRequest(Request):
    def on_json_loading_failed(self, e):
        raise BadRequest('invalid json in request')