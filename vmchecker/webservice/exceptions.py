# -*- coding: utf-8 -*-

from .api import ApiException

class BadRequest(ApiException):
    error_code = 2
    code = 400
    description = 'Bad request.'

class Unauthorized(ApiException):
    error_code = 3
    code = 401
    description = 'You are not authorized.'

class Forbidden(ApiException):
    error_code = 4
    code = 403
    description = 'Forbidden.'

class NotFound(ApiException):
    error_code = 1
    code = 404
    description = 'Resource not found.'





