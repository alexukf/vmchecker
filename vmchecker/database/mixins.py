# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from voluptuous import Schema, Coerce, All
from datetime import datetime

def Date(fmt = '%Y-%m-%d'):
    return lambda v: datetime.strptime(v, fmt)

map_types = {
    'VARCHAR': unicode,
    'INTEGER': int,
    'DATETIME': Date(),
    'FLOAT': float
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
    def add_validator(cls, key, validator):
        cls.v_schema[key].append(validator)

    @classmethod
    def get_schema(cls):
        schema = {}
        for key, value in cls.v_schema.iteritems():
            schema[key] = All(value)

        return Schema(schema)

    @classmethod
    def get_json_keys(cls):
        return cls.json_keys

    def get_json(self):
        json = {}
        for key in self.__class__.json_keys:
            json[key] = getattr(self, key, '')

        return json



