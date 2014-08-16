# -*- coding: utf-8 -*-

from .api import ApiResponse

class Created(ApiResponse):
    default_status = 201

class Accepted(ApiResponse):
    default_status = 202

class Deleted(ApiResponse):
    default_status = 204

class Updated(ApiResponse):
    default_status = 204
