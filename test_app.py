#!/usr/bin/env python
import httplib
import urllib

URL = "localhost:5000"
version = "v1"

def get(conn, url, params = None):
    print "GET %s" % url
    headers = {}
    req_params = ""
    if not params is None:
        headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
        req_params = urllib.urlencode(params)

    conn.request("GET", "/%s%s" % (version, url), req_params, headers)
    reponse = conn.getresponse()
    print reponse.read()

def post(conn, url, params = None):
    print "POST %s" % url
    headers = {}
    req_params = ""
    if not params is None:
        headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
        req_params = urllib.urlencode(params)

    conn.request("POST", "/%s%s" % (version, url), req_params, headers)
    reponse = conn.getresponse()
    print reponse.read()

def put(conn, url, params = None):
    print "PUT %s" % url
    headers = {}
    req_params = ""
    if not params is None:
        headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
        req_params = urllib.urlencode(params)

    conn.request("PUT", "/%s%s" % (version, url), req_params, headers)
    reponse = conn.getresponse()
    print reponse.read()

if __name__ == "__main__":
    conn = httplib.HTTPConnection(URL)
    get(conn, "/courses/")
    post(conn, "/courses/", {
        'name' : 'Sisteme de operare',
        'repository_path' : '/home/so/repo',
        'root_path' : '/home/so'
        })
    get(conn, "/courses/")
    put(conn, "/courses/" , {
        'name' : 'test'
        })
    put(conn, "/courses/1", {
        'repository_path' : '/hacked'
        })
    put(conn, "/courses/1", {
        'name' : 'Sisteme de operare 2.0',
        'repository_path' : '/home/so/git_repo',
        'root_path' : '/home/so2.0'
        })
    get(conn, "/courses/")
    post(conn, "/assignments/", {
        "name" : "Tema 1",
        "deadline" : "2014-03-02",
        "statement_url" : "http://localhost",
        "upload_active_from" : "2014-01-01",
        "upload_active_to" : "2014-04-02",
        "course_id" : 1
        })
    post(conn, "/assignments/", {
        "name" : "Tema 2",
        "deadline" : "2014-03-02",
        "statement_url" : "http://localhost",
        "upload_active_from" : "2014-01-01",
        "upload_active_to" : "2014-04-02",
        "course_id" : 1
        })
    get(conn, "/assignments/")
    get(conn, "/courses/")
