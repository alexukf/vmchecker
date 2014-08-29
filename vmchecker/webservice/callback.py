# -*- coding: utf-8 -*-

from flask import request
from xmlrpclib import ServerProxy, Error
from urlparse import urlparse, urlunparse
import simplejson as json

def mockup_respond(submit):
    assert submit.asynchronous

    # callback_data is json encoded because it's a
    # field in a multipart/form-data request
    callback_data = json.loads(submit.callback_data)

    # callback_data looks like this :
    # key = parameter index in the callback function
    # value = array(name of the parameter, value)
    # if the value of a parameter is set, it must
    # be sent back exactly the same
    params = []
    for idx, param in sorted(callback_data.iteritems()):
        print idx
        if param[0] == 'grade':
            params.append(10)
        elif param[0] == 'comments':
            params.append('swell')
        else:
            params.append(param[1])

    parsed_url = urlparse(submit.callback_url)
    xmlrpcserver_url = urlunparse([
        parsed_url.scheme, submit.callback_host + ':%d' % parsed_url.port,
        parsed_url.path, "", parsed_url.query, ""])

    # create the XMLRPC proxy
    proxy = ServerProxy(submit.callback_url)

    # and call the provided method
    response = proxy.system.multicall([{'methodName': submit.callback_function,
                                        'params': params}])


