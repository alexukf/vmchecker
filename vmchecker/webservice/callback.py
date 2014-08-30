# -*- coding: utf-8 -*-

from flask import request
from xmlrpclib import ServerProxy, Error
from urlparse import urlparse, urlunparse
import simplejson as json

def mockup_respond_xmlrpc(submit):
    assert submit.asynchronous

    #parsed_url = urlparse(submit.callback_url)
    #xmlrpcserver_url = urlunparse([
    #    parsed_url.scheme, submit.callback_host + ':%d' % parsed_url.port,
    #    parsed_url.path, "", parsed_url.query, ""])

    # create the XMLRPC proxy
    proxy = ServerProxy(submit.callback_url)
    print proxy.system.listMethods()
    print proxy.system.methodSignature(submit.callback_fn)

    # we assume that the webservice gets parameters the following
    # way :
    # grade, comments, callback_data (this will be sent back exactly
    # the way it came)
    submit.grade = 10
    submit.comments = u"Foarte bună temă"
    params = [submit.grade, submit.comments, submit.callback_data];

    # and call the provided method
    response = proxy.system.multicall([{'methodName': submit.callback_fn,
                                        'params': params}])
    print response


