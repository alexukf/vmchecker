# -*- coding: utf-8 -*-

from .api import ApiResponse

class Created(ApiResponse):
    default_status = 201

    def __init__(self, message, location):
        content = {
            'message': message,
            'location': location
            }
        ApiResponse.__init__(self, content)

class Accepted(ApiResponse):
    default_status = 202

class Deleted(ApiResponse):
    default_status = 204

class Updated(ApiResponse):
    default_status = 204
