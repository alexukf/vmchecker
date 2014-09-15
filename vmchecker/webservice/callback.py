# -*- coding: utf-8 -*-

from flask import request
from xmlrpclib import ServerProxy, Error
from urlparse import urlparse, urlunparse
import simplejson as json

def mockup_respond_xmlrpc(submit):
    assert submit.asynchronous

    # create the XMLRPC proxy
    proxy = ServerProxy(submit.callback_url)

    # we assume that the webservice gets parameters the following
    # way :
    # grade, comments, callback_data (this will be sent back exactly
    # the way it came)
    submit.grade = 10
    submit.comments = u"Foarte bună temă"
    params = [submit.grade, submit.comments, submit.callback_data];

    # and call the provided method
    proxy.system.multicall([{
        'methodName': submit.callback_fn,
        'params': params
        }])


