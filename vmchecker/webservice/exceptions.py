# -*- coding: utf-8 -*-

from .api import ApiException

class NotFound(ApiException):
    app_code = 1
    code = 404
    description = 'Resource not found.'

class BadRequest(ApiException):
    app_code = 2
    code = 400
    description = 'Bad request.'
