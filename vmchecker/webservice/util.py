from flask import g, jsonify
from database.base import Session
from werkzeug.exceptions import HTTPException
from datetime import datetime

def Date(fmt = '%Y-%m-%d'):
    return lambda v: datetime.strptime(v, fmt)

def get_session():
    session = getattr(g, '_session', None)
    if session is None:
        g._session = session = Session()
    return session

def teardown_session(exception):
    session = getattr(g, '_session', None)
    if session is not None:
        session.close()

def make_json_error(ex):
    description = ex.get_description()
    # remove the <p></p> tags from the description as
    # we return JSON
    description = description[3:len(description) - 4]
    response = jsonify(message = str(ex),
            description = description)
    response.status_code = (ex.code
            if isinstance(ex, HTTPException)
            else 500)
    return response

def make_json_response(message, status_code, headers = None):
    response = jsonify(message)
    response.status_code = status_code
    response.headers = headers
    return response

