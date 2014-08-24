# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, jsonify, request
from endpoints import *

from . import endpoints
from .api import ApiRequest, ApiResponse
from .exceptions import BadRequest
from ..database.util import ApiJSONEncoder

def before_request():
    """This gets executed before the request is passed to the application"""

    # we force the caching of the JSON because flask will not load the
    # JSON unless the mimetype is 'application/json'.
    # XXX If the loading throws an error it will be ignored
    # and request.json will end up being None
    request.get_json(force=True, silent=True)
    return None

def create_webservice():
    app = Flask('vmchecker')
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    for endpoint in endpoints.apis:
        print 'Registering endpoint %s' % endpoint.__name__
        endpoint.register_api_endpoint(blueprint)

    blueprint.before_request(before_request)

    app.register_blueprint(blueprint)

    app.json_encoder = ApiJSONEncoder
    app.request_class = ApiRequest
    app.response_class = ApiResponse

    # TODO overwrite the default exceptions with custom ones

    return app
