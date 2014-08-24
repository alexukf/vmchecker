# -*- coding: utf-8 -*-

from flask.json import JSONEncoder
from datetime import datetime

from .mixins import ApiResource

class ApiJSONEncoder(JSONEncoder):
    """ Custom JSON Encoder to handle API Resources """

    def default(self, obj):
        if isinstance(obj, ApiResource):
            return obj.get_json()
        if isinstance(obj, datetime):
            return obj.strftime('%H:%M %d/%m/%Y')

        return JSONEncoder.default(obj)
