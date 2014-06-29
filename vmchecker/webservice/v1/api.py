from flask.views import MethodView
from webservice.util import get_session

class API(MethodView):
    def __init__(self):
        # the session is closed when the request context
        # is torn down
        self.session = get_session()

    @classmethod
    def register_api_endpoint(cls, app):
        func = cls.as_view(cls.endpoint)
        app.add_url_rule("%s/" % cls.prefix, defaults={ cls.pk["name"]: None },
                view_func = func, methods=["GET"])
        app.add_url_rule("%s/" % cls.prefix,
                view_func = func, methods=["POST"])
        app.add_url_rule("%s/<%s:%s>" % (cls.prefix, cls.pk["type"], cls.pk["name"]),
                view_func = func, methods=["GET", "PUT", "DELETE", "PATCH"])
