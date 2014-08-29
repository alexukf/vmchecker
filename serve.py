#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

from gevent.wsgi import WSGIServer
from vmchecker.webservice import application
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication

def run_gevent_server():
    http_server = WSGIServer(('', 5000), DebuggedApplication(application))
    http_server.serve_forever()

def run_flask_server():
    application.debug = True
    application.run(host='0.0.0.0')

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == 'flask':
        run_flask_server()
    else:
        run_gevent_server()
