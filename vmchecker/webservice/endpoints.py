# -*- coding: utf-8 -*-

import bcrypt
from datetime import datetime
from flask import request, url_for, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from voluptuous import All, Range, Length, MultipleInvalid, Schema, Required

from .auth import require_basic_auth
from .util import MimeType
from .api import Api, ApiResponse
from .exceptions import *
from .responses import *
from ..backend import session_scope
from ..database import models

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

        return ApiResponse({'collection': results})

    @require_basic_auth
    def post(self):
        schema = models.Assignment.get_schema(
            required_keys=['name', 'deadline', 'statement_url',
                           'upload_active_from', 'upload_active_to',
                           'penalty_weight', 'total_points', 'timeout',
                           'course_id'],
            optional_keys=['timedelta', 'storage_type',
                           'machine_id', 'storer_id']
            )
        location = url_for('.' + self.endpoint) + '%d'

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
        schema = models.Assignment.get_schema(
            optional_keys=['name', 'deadline', 'statement_url',
                           'upload_active_from', 'upload_active_to',
                           'timedelta', 'penalty_weight', 'total_points',
                           'timeout', 'storage_type', 'course_id', 'machine_id',
                           'storer_id']
            )

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                        .filter_by(id=assignment_id) \
                        .one()
                result.update(**data)
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

        return ApiResponse({'collection': results})

    @require_basic_auth
    def post(self):
        schema = models.Course.get_schema(
                required_keys=['name', 'repository_path', 'root_path'])
        location = url_for('.' + self.endpoint) + '%d'

        try:
            data = schema(request.json)
            new_course = models.Course(**data)
            with session_scope(self.db) as session:
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
        schema = models.Course.get_schema()

        try:
            data = schema(request.json)
            with session_scope(db) as session:
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

        return ApiResponse({'collection': results})

    @require_basic_auth
    def post(self):
        schema = models.Submit.get_schema(required_keys=['assignment_id'])
        location = url_for('.' + self.endpoint) + '%d'

        file_schema = Schema({
            Required('file'): All(
                MimeType(['application/zip'])
                )
            })

        try:
            data = schema(request.json)
            files = file_schema(request.files.to_dict(flat=True))

            with session_scope(self.db) as session:
                # check if assignment exists
                result = session.query(models.Assignment) \
                                .filter_by(id=data['assignment_id']) \
                                .first()
                if result is None:
                    raise BadRequest("Assignment %d does not exist" % assignment_id)

                # check if upload is permitted
                now = datetime.uctnow()
                if (now < result.upload_active_from) or \
                        (now > result.upload_active_to):
                    raise BadRequest("Upload is only permitted between %s and %s" % \
                            (result.upload_active_from, result.upload_active_to))

                # check if user tried to submit too soon
                result = session.query(models.Submit) \
                                .filter_by(user_id=g.user.id) \
                                .order_by(desc(models.Submit.upload_time)) \
                                .first()
                if result is not None:
                    timedelta = datetime.utcnow() - result.upload_time
                    remaining_time = result.assignment.timedelta - timedelta.total_seconds()
                    if (remaining_time > 0):
                        raise BadRequest("Submitted too soon, please wait %f seconds" % remaining_time)

                new_submit = models.Submit(**data)
                new_submit.filename = files['file'].tmpname

                submit(new_submit)

                self.session.add(new_submit)
            location = location % new_submit.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return Created('Submit created', location)

    @require_basic_auth
    def patch(self, submit_id):
        schema = models.submit.get_schema(required_keys=['grade'],
                optional_keys=['comments'])

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

        return ApiResponse({'collection': results})

    @require_basic_auth
    def post(self):
        schema = models.User.get_schema(
                required_keys=['username', 'password'])
        location = url_for('.' + self.endpoint) + '%d'

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
        schema = models.User.get_schema(required_keys=['password'])

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

apis = [Assignment, Course, Submit, User]
__all__ = map(lambda klazz: klazz.__name__, apis)
