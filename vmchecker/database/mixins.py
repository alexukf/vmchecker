# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from voluptuous import Schema, Coerce, All, Required
from datetime import datetime

def Date(fmt = '%H:%M %d/%m/%Y'):
    return lambda v: datetime.strptime(v, fmt)

map_types = {
    'VARCHAR': unicode,
    'INTEGER': int,
    'DATETIME': Date(),
    'FLOAT': float,
    'BOOLEAN': bool
    }

class ApiResourceMeta(DeclarativeMeta):
    """ Metaclass that is used to """
    def __init__(cls, name, bases, dct):
        cls.v_schema = {}
        cls.json_keys = []

        for key, value in cls.__dict__.iteritems():
            if isinstance(value, Column):
                cls.v_schema[key] = Coerce(map_types[str(value.type)])
                cls.json_keys.append(key)

        super(ApiResourceMeta, cls).__init__(name, bases, dct)

class ApiResource(object):
    def update(self, data):
        for key, value in dict.iteritems(data):
            setattr(self, key, value)

    @classmethod
    def get_schema(cls, required_keys=[], optional_keys=[]):
        schema = {}

        all_keys = frozenset(required_keys + optional_keys)
        for key, value in cls.v_schema.iteritems():
            if all_keys and key not in all_keys:
                continue

            if key in required_keys:
                key = Required(key)

            schema[key] = All(value)

        return schema

    def get_json(self):
        json = {}
        for key in self.__class__.json_keys:
            json[key] = getattr(self, key, '')

        return json



