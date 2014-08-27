#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

from gevent.wsgi import WSGIServer
from vmchecker.webservice import application

http_server = WSGIServer(('', 5000), application)
http_server.serve_forever()
