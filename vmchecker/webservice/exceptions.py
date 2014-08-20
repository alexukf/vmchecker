# -*- coding: utf-8 -*-

from .api import ApiException

class BadRequest(ApiException):
    app_code = 2
    code = 400
    description = 'Bad request.'

class Unauthorized(ApiException):
    app_code = 3
    code = 401
    description = 'You are not authorized.'

class Forbidden(ApiException):
    app_code = 4
    code = 403
    description = 'Forbidden.'

class NotFound(ApiException):
    app_code = 1
    code = 404
    description = 'Resource not found.'





