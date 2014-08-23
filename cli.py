#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import click
import requests
import random
import string
import simplejson as json
from click import STRING, INT, FLOAT, BOOL
from datetime import datetime
from datetime import timedelta
from requests.auth import HTTPBasicAuth

auth=HTTPBasicAuth('admin', '123456')
headers={'Content-Type': 'application/json'}
api_url='http://localhost:5000/api'

class DateParamType(click.ParamType):
    name = 'date'
    fmt = '%H:%M %d/%m/%Y'

    def convert(self, value, param, ctx):
        try:
            date = datetime.strptime(value, self.fmt)
            return value
        except ValueError, e:
            self.fail(str(e), param, ctx)
DATE = DateParamType()

def get_random_string():
    return ''.join(random.choice(string.lowercase) for i in range(10))

def get_random_number():
    return random.randint(0, 10)

def get_random_date(start, end=None):
    if end is not None:
        interval = timedelta(random.randint(0, (end - start).days))
    else:
        interval = timedelta(random.randint(0, 120))

    return (start + interval).str

@click.group()
def commands():
    pass

@commands.group()
def user():
    """Actions available for the user"""
    pass

@user.command(name='add')
@click.option('--username', default=get_random_string(), type=STRING)
@click.password_option(type=STRING)
def add_user(*args, **kw_args):
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.post('%s/users/' % api_url,
                      data=payload,
                      headers=headers,
                      auth=auth)

    print r.json()

@user.command(name='get')
@click.option('--id', type=INT)
def get_user(*args, **kw_args):
    url = '%s/users/' % api_url
    if kw_args['id'] is not None:
        url += kw_args['id']

    r = requests.get(url, headers=headers, auth=auth)

    print r.json()

@user.command(name='edit')
@click.option('--id', prompt=True, type=INT)
@click.password_option(type=STRING)
def edit_user(*args, **kw_args):
    url = '%s/users/%s' % (api_url, kw_args['id'])

    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.patch(url, data=payload, headers=headers, auth=auth)

    print r.json()

@commands.group(name='assignment')
def assignment():
    """Actions available for the assignment"""
    pass

@assignment.command(name='add')
@click.option('--name', prompt=True, type=STRING)
@click.option('--deadline', prompt=True, type=DATE)
@click.option('--statement_url', prompt=True, type=STRING)
@click.option('--upload_active_from', prompt=True, type=DATE)
@click.option('--upload_active_to', prompt=True, type=DATE)
@click.option('--penalty_weight', prompt=True, type=FLOAT)
@click.option('--total_points', prompt=True, type=FLOAT)
@click.option('--timeout', prompt=True, type=FLOAT)
@click.option('--course_id', prompt=True, type=INT)
@click.option('--timedelta', type=FLOAT)
@click.option('--storage_type', type=click.Choice(['normal', 'large']))
@click.option('--machine_id', type=INT)
@click.option('--storer_id', type=INT)
def add_assignment(*args, **kw_args):
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.post('%s/assignments/' % api_url,
                      data=payload, headers=headers, auth=auth)

    print r.json()

@assignment.command(name='get')
@click.option('--id', type=INT)
def get_assignment(*args, **kw_args):
    url = '%s/assignments/' % api_url
    if kw_args['id'] is not None:
        url += kw_args['id']

    r = requests.get(url, headers=headers, auth=auth)

    print r.json()

@assignment.command(name='edit')
@click.option('--id', prompt=True, type=INT)
@click.option('--name', type=STRING)
@click.option('--deadline', type=DATE)
@click.option('--statement_url', type=STRING)
@click.option('--upload_active_from', type=DATE)
@click.option('--upload_active_to', type=DATE)
@click.option('--penalty_weight', type=FLOAT)
@click.option('--total_points', type=FLOAT)
@click.option('--timeout', type=FLOAT)
@click.option('--course_id', type=INT)
@click.option('--timedelta', type=FLOAT)
@click.option('--storage_type', type=click.Choice(['normal', 'large']))
@click.option('--machine_id', type=INT)
@click.option('--storer_id', type=INT)
def edit_assignment(*args, **kw_args):
    url = '%s/assignments/%s' % (api_url, kw_args['id'])

    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.patch(url, data=payload, headers=headers, auth=auth)

    print r.json()

@commands.group()
def course():
    """Actions available for the course"""
    pass

@course.command(name='add')
@click.option('--name', prompt=True, type=STRING)
@click.option('--repository_path', prompt=True, type=STRING)
@click.option('--root_path', prompt=True, type=STRING)
def add_course(*args, **kw_args):
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.post('%s/courses/' % api_url,
                      data=payload,
                      headers=headers,
                      auth=auth)

    print r.json()

@course.command(name='get')
@click.option('--id', type=STRING)
def get_course(*args, **kw_args):
    url = '%s/courses/' % api_url
    if kw_args['id'] is not None:
        url += kw_args['id']

    r = requests.get(url, headers=headers, auth=auth)

    print r.json()

@course.command(name='edit')
@click.option('--id', prompt=True, type=INT)
@click.option('--name', type=STRING)
@click.option('--repository_path', type=STRING)
@click.option('--root_path', type=STRING)
def edit_course(*args, **kw_args):
    url = '%s/courses/%s' % (api_url, kw_args['id'])

    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})

    r = requests.patch(url, data=payload, headers=headers, auth=auth)

    print r.json()

if __name__ == '__main__':
    commands()
