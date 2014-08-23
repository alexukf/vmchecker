# -*- coding: utf-8 -*-

from flask.json import JSONEncoder
from datetime import datetime

from .mixins import ApiResource

class ApiJSONEncoder(JSONEncoder):
    """ Custom JSON Encoder to handle API Resources """

    def default(self, obj):
        if isinstance(obj, ApiResource):
            json = {}
            for key in obj.__class__.get_json_keys():
                json[key] = self.default(getattr(obj, key, ''))
            return json
        if isinstance(obj, datetime):
            return obj.strftime('%H:%M %d/%m/%Y')

        return JSONEncoder.default(obj)
