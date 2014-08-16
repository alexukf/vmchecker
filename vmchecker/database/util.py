# -*- coding: utf-8 -*-

from .mixins import ApiResource
from flask.json import JSONEncoder

class ApiJSONEncoder(JSONEncoder):
    """ Custom JSON Encoder to handle API Resources """

    def default(self, obj):
        if isinstance(obj, ApiResource):
            print obj
            json = {}
            for key in obj.__class__.get_json_keys():
                json[key] = getattr(obj, key, '')
            return json
        return JSONEncoder.default(obj)
