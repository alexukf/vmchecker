# -*- coding: utf-8 -*-

import bcrypt
from datetime import datetime
from flask import request, url_for, g
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.orm.exc import NoResultFound
from voluptuous import All, Range, Length, MultipleInvalid, Schema, Required

from .. import submit
from .auth import require_basic_auth
from .util import MimeType
from .api import Api, ApiResponse
from .exceptions import *
from .responses import *
from ..backend import session_scope
from ..database import models

from .callback import mockup_respond

class Assignment(Api):
    endpoint = 'assignment_api'
    prefix = '/assignments'
    pk = {'name' : 'assignment_id', 'type' : 'int'}

    def get(self, assignment_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Assignment);

            if assignment_id is not None:
                query = query.filter_by(id=assignment_id)

            results = map(lambda el: el.get_json(), query.all())

        if assignment_id is not None and not results:
            raise NotFound("Assignment %d was not found" % assignment_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = models.Assignment.get_schema(keys=[
            'name', 'display_name', 'deadline', 'statement_url',
            'upload_active_from', 'upload_active_to',
            'penalty_weight', 'penalty_limit', 'total_points', 'timeout',
            'course_id'])
        schema.update(models.Assignment.get_schema(keys=[
            'timedelta', 'storage_type', 'machine_id', 'storer_id'],
            required=False))
        schema = Schema(schema)

        try:
            data = schema(request.json)
            new_assignment = models.Assignment(**data)
            with session_scope(self.db) as session:
                course_id = new_assignment.course_id
                query = session.query(models.Course) \
                               .filter_by(id=course_id)
                if not query.first():
                    raise BadRequest("Course %d does not exist" % course_id)
                session.add(new_assignment)
            location = location % new_assignment.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Assignment was created', location)

    @require_basic_auth
    def delete(self, assignment_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                        .filter_by(id=assignment_id) \
                        .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Assignment %d was not found" % assignment_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Deleted('Assignment %d was deleted' % assignment_id)

    @require_basic_auth
    def patch(self, assignment_id):
        schema = Schema(models.Assignment.get_schema(keys=[
            'name', 'display_name', 'deadline', 'statement_url',
            'upload_active_from', 'upload_active_to',
            'timedelta', 'penalty_weight', 'penalty_limit', 'total_points',
            'timeout', 'storage_type', 'course_id', 'machine_id',
            'storer_id'], required=False))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                                .filter_by(id=assignment_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Assignment %d was not found" % assignment_id)
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Updated("Assignment %d was updated" % assignment_id)

class Course(Api):
    endpoint = 'course_api'
    prefix = '/courses'
    pk = {'name': 'course_id', 'type': 'int'}

    def get(self, course_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Course)

            if course_id is not None:
                query = query.filter_by(id=course_id)

            results = map(lambda el: el.get_json(), query.all())

        if course_id is not None and not results:
            raise NotFound("Course %d was not found" % course_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = Schema(models.Course.get_schema(keys=[
            'name', 'repository_path', 'root_path']))

        try:
            data = schema(request.json)
            new_course = models.Course(**data)
            with session_scope(self.db) as session:
                pass
                session.add(new_course)
            location = location % new_course.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Course was created', location)

    @require_basic_auth
    def delete(self, course_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Course) \
                                .filter_by(id=course_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Course %d was not found" % assignment_id)
        except IntegrityError:
            raise BadRequest(str(e))

        return Deleted('Course %d was deleted' % course_id)

    @require_basic_auth
    def patch(self, course_id):
        schema = Schema(models.Course.get_schema(required=False))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Course) \
                                .filter_by(id=course_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Course %d was not found" % assignment_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Course %d was updated" % course_id)

class Submit(Api):
    endpoint = 'submit_api'
    prefix = '/submits'
    pk = {'name': 'submit_id', 'type': 'int'}

    @require_basic_auth
    def get(self, submit_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Submit).filter_by(user_id=g.user.id)

            if submit_id is not None:
                query = query.filter_by(id=submit_id)

            results = map(lambda el: el.get_json(), query.all())

        if submit_id is not None and not results:
            raise NotFound("Submit %d was not found" % submit_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = models.Submit.get_schema(keys=['assignment_id'])
        schema.update(models.Submit.get_schema(
            keys=['callback_url', 'callback_port', 'callback_type',
                'callback_function', 'callback_data'],
            required=False))
        schema = Schema(schema)

        file_schema = Schema({
            Required('file'): All(MimeType([
                'application/zip'
                ]))
            })

        try:
            # we can't piggy back JSON because we're using multipart/form-data
            # for the file upload so we use multipart/form-data for
            # passing the assignment_id as well
            data = schema(request.form.to_dict(flat=True))
            files = file_schema(request.files.to_dict(flat=True))

            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                                .filter_by(id=data['assignment_id']) \
                                .first()
                if result is None:
                    raise BadRequest("Assignment %d does not exist" % data['assignment_id'])

                # check if upload is permitted
                now = datetime.utcnow()
                if (now < result.upload_active_from) or \
                        (now > result.upload_active_to):
                    raise BadRequest("Upload is only permitted between %s and %s" % \
                            (result.upload_active_from, result.upload_active_to))

                # check if user tried to submit too soon
                result = session.query(models.Submit) \
                                .filter_by(user_id=g.user.id) \
                                .order_by(desc(models.Submit.upload_time)) \
                                .first()
                if False and result is not None:
                    timedelta = datetime.utcnow() - result.upload_time
                    remaining_time = result.assignment.timedelta - timedelta.total_seconds()
                    if (remaining_time > 0):
                        raise BadRequest("Submitted too soon, please wait %f seconds" % remaining_time)

                new_submit = models.Submit(**data)


                new_submit.filename = files['file']['tmpname']
                new_submit.mimetype = files['file']['mimetype']
                new_submit.user_id = g.user.id
                new_submit.upload_time = now

                # force sqlalchemy to load the relationships
                session.enable_relationship_loading(new_submit)
                #submit.submit(new_submit)

                if 'callback_url' in data:
                    new_submit.callback_host = request.remote_addr
                    new_submit.asynchronous = True
                    mockup_respond(new_submit)

                session.add(new_submit)
            location = location % new_submit.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))
        except ValueError:
            raise BadRequest('backend failed to submit')

        return Created('Submit created', location)

    @require_basic_auth
    def patch(self, submit_id):
        schema = models.Submit.get_schema(
            keys=['grade', 'comments'], required=False)
        schema = Schema(schema)

        try:
            data = schema(request.json)

            with session_scope(self.db) as session:
                result = session.query(models.Submit) \
                                .filter_by(id=submit_id) \
                                .first()
                if result is None:
                    raise NotFound("Submit %d does not exist" % submit_id)

                result.update(data)
        except MultipleInvalid, e:
            raise BadRequest(str(e))
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Submit %d was updated" % submit_id)

    @classmethod
    def register_api_endpoint(cls, app):
        """ Register an endpoint to the flask application """
        func = cls.as_view(cls.endpoint)
        app.add_url_rule("%s/" % cls.prefix, defaults={cls.pk["name"]: None},
                view_func=func, methods=["GET"])
        app.add_url_rule("%s/" % cls.prefix,
                view_func=func, methods=["POST"])
        app.add_url_rule("%s/<%s:%s>" % (cls.prefix, cls.pk['type'], cls.pk['name']),
                view_func=func, methods=["GET", "PATCH"])

class User(Api):
    endpoint = 'user_api'
    prefix = '/users'
    pk = {'name': 'user_id', 'type': 'int'}

    @require_basic_auth
    def get(self, user_id):
        results = []

        if user_id != g.user.id:
            raise Forbidden()

        with session_scope(self.db) as session:
            query = session.query(models.User)

            if user_id is not None:
                query = query.filter_by(id=user_id)

            results = map(lambda el: el.get_json(), query.all())

        if user_id is not None and not results:
            raise NotFound("User %d was not found" % user_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = Schema(models.User.get_schema(keys=['username', 'password']))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'),
                                                 bcrypt.gensalt())
                new_user = models.User(**data)
                session.add(new_user)
            location = location % new_user.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('User created', location)

    @require_basic_auth
    def delete(self, user_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.User) \
                                .filter_by(id=user_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("User %d was not found" % user_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Deleted("User %d was deleted" % user_id)

    @require_basic_auth
    def patch(self, user_id):
        schema = Schema(models.User.get_schema(keys=['password'], required=False))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.User) \
                                .filter_by(id=user_id) \
                                .one()
                data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'),
                                                 bcrypt.gensalt())
                result.update(data)
        except NoResultFound:
            raise NotFound("User %d was not found" % user_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("User %d was updated" % user_id)

class Machine(Api):
    endpoint = 'machine_api'
    prefix = '/machines'
    pk = {'name': 'machine_id', 'type': 'int'}

    machine_cfg = {
        'vmware': {
            'class': models.VMwareMachine,
            'required_keys': [],
            'optional_keys': []
            }
        }
    required_keys = ['hostname', 'vmx_path', 'user', 'password',
        'base_path', 'shell_path', 'home_in_shell',
        'tester_id', 'type']
    optional_keys = ['build_script', 'run_script']

    @require_basic_auth
    def get(self, machine_id):
        results = []

        derived_classes = [v['class'] for v in self.machine_cfg.itervalues()]

        with session_scope(self.db) as session:
            query = session.query(with_polymorphic(models.Machine, derived_classes))

            if machine_id is not None:
                query = query.filter_by(id=machine_id)

            results = map(lambda el: el.get_json(), query.all())

        if machine_id is not None and not results:
            raise NotFound("Machine %d was not found" % machine_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'

        if 'type' not in request.json:
            raise BadRequest('type column is required')
        type = request.json['type']

        machine_cfg = self.machine_cfg[type]
        clazz = machine_cfg['class']
        schema = models.Machine.get_schema(keys=self.required_keys)
        schema.update(models.Machine.get_schema(
            keys=self.optional_keys, required=False))
        schema.update(clazz.get_schema(keys=machine_cfg['required_keys']))
        schema.update(clazz.get_schema(
            keys=machine_cfg['optional_keys'], required=False))
        schema = Schema(schema)

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                new_machine = clazz(**data)
                session.add(new_machine)
            location = location % new_machine.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Machine created', location)

    @require_basic_auth
    def delete(self, machine_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Machine) \
                                .filter_by(id=machine_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Machine %d was not found" % machine_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Deleted("Machine %d was deleted" % machine_id)

    @require_basic_auth
    def patch(self, machine_id):
        if 'type' not in request.json:
            raise BadRequest('type column is required')
        type = request.json['type']

        machine_cfg = self.machine_cfg[type]
        clazz = machine_cfg['class']
        schema = models.Machine.get_schema(
                keys=self.required_keys, required=False)
        schema.update(models.Machine.get_schema(
            keys=self.optional_keys, required=False))
        schema.update(clazz.get_schema(
            keys=machine_cfg['required_keys'], required=False))
        schema.update(clazz.get_schema(
            keys=machine_cfg['optional_keys'], required=False))
        schema = Schema(schema)

        derived_classes = [v['class'] for v in self.machine_cfg.itervalues()]

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(with_polymorphic(models.Machine, derived_classes)) \
                                .filter_by(id=machine_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Machine %d was not found" % machine_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Machine %d was updated" % machine_id)

class Tester(Api):
    endpoint = 'tester_api'
    prefix = '/testers'
    pk = {'name': 'tester_id', 'type': 'int'}

    tester_cfg = {
        'vmwareserver': {
            'class': models.VMwareTester,
            'required_keys': ['url', 'port', 'username', 'password',
                              'use_datastore', 'datastore_name',
                              'datastore_path'],
            'optional_keys': []
            }
        }
    required_keys = ['login_username', 'hostname', 'queue_path', 'type']
    optional_keys = []

    @require_basic_auth
    def get(self, tester_id):
        results = []

        derived_classes = [v['class'] for v in self.tester_cfg.itervalues()]

        with session_scope(self.db) as session:
            query = session.query(with_polymorphic(models.Tester, derived_classes))

            if tester_id is not None:
                query = query.filter_by(id=tester_id)

            results = map(lambda el: el.get_json(), query.all())

        if tester_id is not None and not results:
            raise NotFound("Machine %d was not found" % tester_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'

        if 'type' not in request.json:
            raise BadRequest('type column is required')
        type = request.json['type']

        tester_cfg = self.tester_cfg[type]
        clazz = tester_cfg['class']
        schema = models.Tester.get_schema(keys=self.required_keys)
        schema.update(models.Tester.get_schema(
            keys=self.optional_keys, required=False))
        schema.update(clazz.get_schema(keys=tester_cfg['required_keys']))
        schema.update(clazz.get_schema(
            keys=tester_cfg['optional_keys'], required=False))
        schema = Schema(schema)

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                new_tester = clazz(**data)
                session.add(new_tester)
            location = location % new_tester.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Tester created', location)

    @require_basic_auth
    def delete(self, tester_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Tester) \
                                .filter_by(id=tester_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Tester %d was not found" % tester_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Deleted("Tester %d was deleted" % tester_id)

    @require_basic_auth
    def patch(self, tester_id):
        if 'type' not in request.json:
            raise BadRequest('type column is required')
        type = request.json['type']

        tester_cfg = self.tester_cfg[type]
        clazz = tester_cfg['class']
        schema = models.Tester.get_schema(
                keys=self.required_keys, required=False)
        schema.update(models.Tester.get_schema(
            keys=self.optional_keys, required=False))
        schema.update(clazz.get_schema(
            keys=tester_cfg['required_keys'], required=False))
        schema.update(clazz.get_schema(
            keys=tester_cfg['optional_keys'], required=False))
        schema = Schema(schema)

        derived_classes = [v['class'] for v in self.tester_cfg.itervalues()]

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(with_polymorphic(models.Tester, derived_classes)) \
                                .filter_by(id=tester_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Tester %d was not found" % tester_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Tester %d was updated" % tester_id)

class Holiday(Api):
    endpoint = 'holiday_api'
    prefix = '/holidays'
    pk = {'name': 'holiday_id', 'type': 'int'}

    def get(self, holiday_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Holiday)

            if holiday_id is not None:
                query = query.filter_by(id=holiday_id)

            results = map(lambda el: el.get_json(), query.all())

        if holiday_id is not None and not results:
            raise NotFound("Holiday %d was not found" % holiday_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = Schema(models.Holiday.get_schema(
            keys=['start', 'end']))

        try:
            data = schema(request.json)
            new_holiday = models.Holiday(**data)
            with session_scope(self.db) as session:
                session.add(new_holiday)
            location = location % new_holiday.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Holiday was created', location)

    @require_basic_auth
    def delete(self, holiday_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Holiday) \
                                .filter_by(id=holiday_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Holiday %d was not found" % holiday_id)
        except IntegrityError:
            raise BadRequest(str(e))

        return Deleted('Holiday %d was deleted' % holiday_id)

    @require_basic_auth
    def patch(self, holiday_id):
        schema = Schema(models.Holiday.get_schema(
            keys=['start', 'end'], required=False))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Holiday) \
                                .filter_by(id=holiday_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Holiday %d was not found" % holiday_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Holiday %d was updated" % holiday_id)

class Storer(Api):
    endpoint = 'storer_api'
    prefix = '/storers'
    pk = {'name': 'storer_id', 'type': 'int'}

    def get(self, storer_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Storer)

            if storer_id is not None:
                query = query.filter_by(id=storer_id)

            results = map(lambda el: el.get_json(), query.all())

        if storer_id is not None and not results:
            raise NotFound("Storer %d was not found" % storer_id)

        return ApiResponse(results)

    @require_basic_auth
    def post(self):
        location = url_for('.' + self.endpoint) + '%d'
        schema = Schema(models.Storer.get_schema(
            keys=['username', 'hostname']))

        try:
            data = schema(request.json)
            new_storer = models.Storer(**data)
            with session_scope(self.db) as session:
                session.add(new_storer)
            location = location % new_storer.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Storer was created', location)

    @require_basic_auth
    def delete(self, storer_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Storer) \
                                .filter_by(id=storer_id) \
                                .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("Storer %d was not found" % storer_id)
        except IntegrityError:
            raise BadRequest(str(e))

        return Deleted('Storer %d was deleted' % storer_id)

    @require_basic_auth
    def patch(self, storer_id):
        schema = Schema(models.Storer.get_schema(
            keys=['username', 'hostname'], required=False))

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Storer) \
                                .filter_by(id=storer_id) \
                                .one()
                result.update(data)
        except NoResultFound:
            raise NotFound("Storer %d was not found" % storer_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return Updated("Storer %d was updated" % storer_id)

apis = [Assignment, Course, Submit, User,
        Machine, Tester, Holiday, Storer]
__all__ = map(lambda klazz: klazz.__name__, apis)
