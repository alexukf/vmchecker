#!/usr/bin/env python2
# -*- coding: utf8 -*-

import os
from vmchecker.webservice import application
from vmchecker import backend

if __name__ == '__main__':
    db = backend.get_db()
    db.initialize_db()
    application.config.update(
        DEBUG = True,
        UPLOAD_FOLDER = os.path.join(application.instance_path, 'uploads')
        )
    application.run(host = "0.0.0.0")
