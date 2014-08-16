# -*- coding: utf-8 -*-

from __future__ import with_statement

from . import endpoints
from .api import ApiRequest, ApiResponse
from .exceptions import BadRequest
from ..database.util import ApiJSONEncoder
from flask import Flask, Blueprint, jsonify, request
from endpoints import *

def check_request():
    #check_methods = ['POST', 'PUT', 'PATCH']
    #if request.method not in check_methods:
    #    return None

    mimetype = request.mimetype
    if mimetype.startswith('application/') and mimetype.endswith('json'):
        return None

    try:
        if request.get_json(force=True) is not None:
            return None
    except:
        pass

    raise BadRequest('we only accept json')

def create_webservice():
    app = Flask('vmchecker')
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    for endpoint in endpoints.apis:
        print 'Registering endpoint %s' % endpoint.__name__
        endpoint.register_api_endpoint(blueprint)

    blueprint.before_request(check_request)

    app.register_blueprint(blueprint)

    app.json_encoder = ApiJSONEncoder
    app.request_class = ApiRequest
    app.response_class = ApiResponse

    return app
