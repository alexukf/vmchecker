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

def get(endpoint):
    url = "%s/%s" % (api_url, endpoint)
    response = requests.get(url, auth=auth)
    return response.json()

def post(endpoint, payload, files=None):
    url = "%s/%s" % (api_url, endpoint)
    if files is not None:
        response = requests.post(url, data=payload, auth=auth, files=files)
    else:
        response = requests.post(url, data=payload, auth=auth)
    return response.json()

def patch(endpoint, payload):
    url = "%s/%s" % (api_url, endpoint)
    response = requests.patch(url, data=payload, auth=auth)
    if not response.ok:
        return response.json()
    return '%s was updated' % endpoint

def delete(endpoint):
    url = "%s/%s" % (api_url, endpoint)
    response = requests.delete(url, auth=auth)
    if not response.ok:
        return response.json()
    return '%s was deleted' % endpoint

class DateParamType(click.ParamType):
    """Date parameter type for click"""
    name = 'date'

    # this format must be kept in sync with the Date
    # validator in vmchecker.database.mixins
    fmt = '%H:%M %d/%m/%Y'

    def __init__(self, fmt=None):
        if fmt is not None:
            self.fmt = fmt
        click.ParamType.__init__(self)

    def convert(self, value, param, ctx):
        try:
            date = datetime.strptime(value, self.fmt)
            return date.strftime(self.__class__.fmt)
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

    return (start + interval).strftime("%H:%M %d/%m/%Y")

@click.group()
def commands():
    pass

@commands.group()
def user():
    """Actions available for the user"""
    pass

@user.command(name='get')
@click.option('--id', type=INT)
def get_user(*args, **kw_args):
    """Get users"""
    url = 'users/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@user.command(name='add')
@click.option('--username', default=get_random_string(), type=STRING,
    required=True)
@click.option('--password', default='123456', type=STRING,
    required=True)
def add_user(*args, **kw_args):
    """Add a new user"""
    url = 'users/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@user.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--password', type=STRING, required=True)
def edit_user(*args, **kw_args):
    """Edit a user"""
    url = 'users/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@commands.group(name='assignment')
def assignment():
    """Actions available for the assignment"""
    pass

@assignment.command(name='get')
@click.option('--id', type=INT)
def get_assignment(*args, **kw_args):
    """Get assignments"""
    url = 'assignments/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@assignment.command(name='add')
@click.option('--name', type=STRING, default=get_random_string(), required=True)
@click.option('--display_name', type=STRING, default=get_random_string(),
             required=True)
@click.option('--deadline', type=DATE, default=get_random_date(
    datetime.utcnow(), datetime.utcnow() + timedelta(120)), required=True)
@click.option('--statement_url', type=STRING, default=get_random_string(),
    required=True)
@click.option('--upload_active_from', type=DATE, default=get_random_date(
    datetime.utcnow(), datetime.utcnow()), required=True)
@click.option('--upload_active_to', type=DATE, default=get_random_date(
    datetime.utcnow(), datetime.utcnow() + timedelta(180)), required=True)
@click.option('--penalty_weight', type=FLOAT, default=0.5, required=True)
@click.option('--penalty_limit', type=FLOAT, default=3, required=True)
@click.option('--total_points', type=FLOAT, default=100.0, required=True)
@click.option('--timeout', type=FLOAT, default=300.0, required=True)
@click.option('--course_id', type=INT, required=True)
@click.option('--timedelta', type=FLOAT)
@click.option('--storage_type', type=click.Choice(['normal', 'large']),
        default='normal')
@click.option('--machine_id', type=INT)
@click.option('--storer_id', type=INT)
def add_assignment(*args, **kw_args):
    """Add a new assignment"""
    url = 'assignments/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@assignment.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--name', type=STRING)
@click.option('--deadline', type=DATE)
@click.option('--statement_url', type=STRING)
@click.option('--upload_active_from', type=DATE)
@click.option('--upload_active_to', type=DATE)
@click.option('--penalty_weight', type=FLOAT)
@click.option('--penalty_limit', type=FLOAT)
@click.option('--total_points', type=FLOAT)
@click.option('--timeout', type=FLOAT)
@click.option('--course_id', type=INT)
@click.option('--timedelta', type=FLOAT)
@click.option('--storage_type', type=click.Choice(['normal', 'large']))
@click.option('--machine_id', type=INT)
@click.option('--storer_id', type=INT)
def edit_assignment(*args, **kw_args):
    """Edit an assignment"""
    url = 'assignments/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@commands.group()
def course():
    """Actions available for the course"""
    pass

@course.command(name='get')
@click.option('--id', type=STRING)
def get_course(*args, **kw_args):
    """Get courses"""
    url = 'courses/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@course.command(name='add')
@click.option('--name', type=STRING, default=get_random_string(), required=True)
@click.option('--repository_path', type=STRING, default=get_random_string(),
    required=True)
@click.option('--root_path', type=STRING, default=get_random_string(),
    required=True)
def add_course(*args, **kw_args):
    """Add a new course"""
    url = 'courses/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@course.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--name', type=STRING)
@click.option('--repository_path', type=STRING)
@click.option('--root_path', type=STRING)
def edit_course(*args, **kw_args):
    """Edit a course"""
    url = 'courses/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@commands.group()
def submit():
    """Actions available for the submit"""
    pass

@submit.command(name='get')
@click.option('--id', type=INT)
def get_submit(*args, **kw_args):
    """Get submits"""
    url = 'submits/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])

    print get(url)

@submit.command(name='add')
@click.option('--assignment_id', type=INT, required=True)
@click.argument('file', type=click.File('rb'), required=True)
def add_submit(*args, **kw_args):
    """Submit an assignment"""
    url = 'submits/'
    file = kw_args['file']

    del kw_args['file']
    payload = {k: v for k, v in kw_args.iteritems() if v is not None}
    print post(url, payload, files={'file': file})

@submit.command(name='grade')
@click.option('--id', type=INT, required=True)
@click.argument('grade', type=FLOAT)
@click.argument('comments', type=STRING, required=False)
def grade_submit(*args, **kw_args):
    """Grade a submitted assignment"""
    url = 'submits/%d' % kw_args['id']
    del kw_args['id']

    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@commands.group()
def machine():
    """Actions available for machines"""
    pass

@machine.command(name='get')
@click.option('--id', type=INT)
def get_machine(*args, **kw_args):
    url = 'machines/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])

    print get(url)

@machine.command(name='add')
@click.option('--hostname', type=STRING, default=get_random_string(), required=True)
@click.option('--vmx_path', type=STRING, default=get_random_string(), required=True)
@click.option('--user', type=STRING, default=get_random_string(), required=True)
@click.option('--password', type=STRING, default=get_random_string(), required=True)
@click.option('--base_path', type=STRING, default=get_random_string(), required=True)
@click.option('--shell_path', type=STRING, default=get_random_string(), required=True)
@click.option('--home_in_shell', type=STRING, default=get_random_string(), required=True)
@click.option('--build_script', type=STRING)
@click.option('--run_script', type=STRING)
@click.option('--type', type=STRING, default='vmware')
@click.option('--tester_id', type=INT, required=True)
def add_machine(*args, **kw_args):
    url = 'machines/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@machine.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--hostname', type=STRING)
@click.option('--vmx_path', type=STRING)
@click.option('--user', type=STRING)
@click.option('--password', type=STRING)
@click.option('--base_path', type=STRING)
@click.option('--shell_path', type=STRING)
@click.option('--home_in_shell', type=STRING)
@click.option('--build_script', type=STRING)
@click.option('--run_script', type=STRING)
def edit_machine(*args, **kw_args):
    url = 'machines/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@commands.group()
def tester():
    """Commands available for testers"""
    pass

@tester.command(name='get')
@click.option('--id', type=INT)
def get_tester(*args, **kw_args):
    url = 'testers/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@tester.command(name='add')
@click.option('--hostname', type=STRING, default=get_random_string(), required=True)
@click.option('--queue_path', type=STRING, default=get_random_string(), required=True)
@click.option('--type', type=STRING, default='vmwareserver', required=True)
@click.option('--url', type=STRING, default=get_random_string(), required=True)
@click.option('--port', type=INT, default=get_random_number(), required=True)
@click.option('--username', type=STRING, default=get_random_string(), required=True)
@click.option('--password', type=STRING, default=get_random_string(), required=True)
@click.option('--use_datastore', type=BOOL, default=True, required=True)
@click.option('--datastore_name', type=STRING, default=get_random_string(), required=True)
@click.option('--datastore_path', type=STRING, default=get_random_string(), required=True)
def add_tester(*args, **kw_args):
    url = 'testers/'

    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@tester.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--hostname', type=STRING, default=get_random_string())
@click.option('--queue_path', type=STRING, default=get_random_string())
@click.option('--type', type=STRING, default='vmwareserver')
@click.option('--url', type=STRING, default=get_random_string())
@click.option('--port', type=INT, default=get_random_number())
@click.option('--username', type=STRING, default=get_random_string())
@click.option('--password', type=STRING, default=get_random_string())
@click.option('--use_datastore', type=BOOL, default=True)
@click.option('--datastore_name', type=STRING, default=get_random_string())
@click.option('--datastore_path', type=STRING, default=get_random_string())
def edit_tester(*args, **kw_args):
    url = 'testers/%d' % kw_args['id']
    del kw_args['id']

    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@tester.command(name='delete')
@click.option('--id', type=INT, required=True)
def delete_tester(*args, **kw_args):
    url = 'testers/%d' % kw_args['id']
    print delete(url)

@commands.group()
def holiday():
    """Commands available for the holidays"""
    pass

@holiday.command(name='get')
@click.option('--id', type=INT)
def get_holiday(*args, **kw_args):
    url = 'holidays/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@holiday.command(name='add')
@click.option('--start', type=DateParamType('%d/%m/%Y'), required=True)
@click.option('--end', type=DateParamType('%d/%m/%Y'), required=True)
def add_holiday(*args, **kw_args):
    url = 'holidays/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@holiday.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--start', type=DateParamType('%d/%m/%Y'))
@click.option('--end', type=DateParamType('%d/%m/%Y'))
def edit_holiday(*args, **kw_args):
    url = 'holidays/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@holiday.command(name='delete')
@click.option('--id', type=INT, required=True)
def delete_holiday(*args, **kw_args):
    url = 'holidays/%d' % kw_args['id']
    print delete(url)

@commands.group()
def storer():
    """Commands available for the storers"""
    pass

@storer.command(name='get')
@click.option('--id', type=INT)
def get_storer(*args, **kw_args):
    url = 'storers/'
    if kw_args['id'] is not None:
        url += str(kw_args['id'])
    print get(url)

@storer.command(name='add')
@click.option('--hostname', type=STRING, default=get_random_string(), required=True)
@click.option('--username', type=STRING, default=get_random_string(), required=True)
def add_storer(*args, **kw_args):
    url = 'storers/'
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print post(url, payload)

@storer.command(name='edit')
@click.option('--id', type=INT, required=True)
@click.option('--hostname', type=STRING)
@click.option('--username', type=STRING)
def edit_storer(*args, **kw_args):
    url = 'storers/%d' % kw_args['id']
    del kw_args['id']
    payload = json.dumps({k: v for k, v in kw_args.iteritems() if v is not None})
    print patch(url, payload)

@storer.command(name='delete')
@click.option('--id', type=INT, required=True)
def delete_storer(*args, **kw_args):
    url = 'storers/%d' % kw_args['id']
    print delete(url)

if __name__ == '__main__':
    commands()
