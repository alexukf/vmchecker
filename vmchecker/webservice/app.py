# -*- coding: utf-8 -*-

from __future__ import with_statement

from . import endpoints
from .api import ApiRequest
from ..database.util import ApiJSONEncoder
from flask import Flask, Blueprint, jsonify, request
from werkzeug.exceptions import default_exceptions, HTTPException, BadRequest
from endpoints import *

def make_json_error(ex):
    if isinstance(ex, HTTPException):
        description = ex.get_description()
        # remove the <p> tag from the description because
        # we return JSON
        description = description[len("<p>"):-len("</p>")]
        response = jsonify(message=str(ex),
                           description=description)
        response.status_code = ex.code
        import sys,traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
    else:
        response = jsonifiy(message=str(ex))
        response.status_code = 500

    return response

def check_request():
    check_methods = ['POST', 'PUT', 'PATCH']
    if request.method not in check_methods:
        return None

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

    # register new error handlers that return json
    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    app.json_encoder = ApiJSONEncoder
    app.request_class = ApiRequest

    return app
