#!/usr/bin/env python

import os
from flask import Flask
from werkzeug.exceptions import default_exceptions
from webservice.v1.blueprint import register_blueprint
from webservice.util import make_json_error, teardown_session
from database.util import create_sqlite_db
from database.base import Session
from database.user import User

app = Flask(__name__, instance_relative_config = True, instance_path = '/vagrant')
app.teardown_appcontext(teardown_session)

# register new error handlers that return json
for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

register_blueprint(app)

Session.configure(bind = create_sqlite_db())

if __name__ == '__main__':
    user = User(username = "Adila")
    session = Session()
    session.add(user)
    session.commit()
    app.config.update(
        DEBUG = True,
        UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
        )
    app.run(host = "0.0.0.0")
