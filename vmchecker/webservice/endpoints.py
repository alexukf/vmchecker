from ..backend import session_scope
from ..database import models
from .util import MimeType, make_json_response
from .api import Api

from datetime import datetime
from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound
from voluptuous import All, Range, Length, MultipleInvalid, Schema, Required

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
            raise NotFound("assignment %d not found" % assignment_id)

        return make_json_response({'collection': results}, 200)

    def post(self):
        schema = models.Assignment.get_schema()
        new_assignment_id = None

        try:
            data = schema(request.json)
            new_assignment = models.Assignment(**data)
            with session_scope(self.db) as session:
                session.add(new_assignment)
                new_assignment_id = new_assignment.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message': "assignment added"
            },
            200)

    def delete(self, assignment_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                        .filter_by(id=assignment_id) \
                        .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("assignment %d not found" % assignment_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message': "assignment %d deleted" % assignment_id
            },
            200)

    def put(self, assignment_id):
        self.patch(assignment_id)

    def patch(self, assignment_id):
        schema = models.Assignment.get_schema()

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                        .filter_by(id=assignment_id) \
                        .one()
                result.update(**data)
        except NoResultFound:
            raise NotFound("assignment %d not found" % assignment_id)
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message' : "assignment %d updated" % assignment_id
            },
            200)

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
            raise NotFound("course %d not found" % course_id)

        return make_json_response({'collection': results}, 200)

    def post(self):
        schema = models.Course.get_schema()
        new_course_id = None

        try:
            data = schema(request.json)
            new_course = models.Course(**data)
            with session_scope(self.db) as session:
                session.add(new_course)
                new_course_id = new_course.id
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message' : "course added"
            },
            200)

    def delete(self, course_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.Course) \
                        .filter_by(id=course_id) \
                        .one()
                session.delete(result)
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message': "course %d deleted" % course_id
            },
            200)

    def put(self, course_id):
        self.patch(course_id)

    def patch(self, course_id):
        schema = models.Course.get_schema()

        try:
            data = schema(request.json)
            with session_scope(db) as session:
                result = session.query(models.Course) \
                        .filter_by(id=course_id) \
                        .one()
                result.update(**data)
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

class Submit(Api):
    endpoint = 'submit_api'
    prefix = '/submits'
    pk = {'name': 'submit_id', 'type': 'int'}

    def get(self, submit_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.Submit)

            if submit_id is not None:
                query = query.filter_by(id=submit_id)

            results = map(lambda el: el.get_json(), query.all())

        if submit_id is not None and not results:
            raise NotFound("submit %d was not found" % submit_id)

        return make_json_response({'collection': results}, 200)

    def post(self):
        schema = models.Submit.get_schema()

        file_schema = Schema({
            Required('file'): All(
                MimeType(['application/zip'])
                )
            })

        try:
            data = schema(request.json)
            files = file_schema(request.files.to_dict(flat = True))

            with session_scope(self.db) as session:
                result = session.query(models.Assignment) \
                        .filter_by(id=data['assignment_id']).first()
                if result is None:
                    raise BadRequest("assignment %d not found" % assignment_id)

                now = datetime.uctnow()
                if (now < result.upload_active_from) or \
                        (now > result.upload_active_to):
                    raise BadRequest("upload is permitted between %s and %s" % \
                            (result.upload_active_from, result.upload_active_to))

                result = session.query(models.Submit) \
                        .filter_by(user_id=data['user_id']) \
                        .order_by(desc(models.Submit.upload_time)).first()
                if result is not None:
                    timedelta = datetime.datetime.utcnow() - result.upload_time
                    remaining_time = result.assignment.timedelta - timedelta.total_seconds()
                    if (remaining_time > 0):
                        raise BadRequest("submitted too soon, please wait %f seconds" % remaining_time)

                new_submit = models.Submit(**data)
                new_submit.filename = files['file'].tmpname

                #submit(new_submit.filename, new_submit)

                self.session.add(new_submit)
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        #try:
        #    submit.submit(new_submit.filename, new_submit.assignment_id,
        #            new_submit.user.username, new_submit.assignment.course_id)

        return make_json_response({
            'message' : "submit added"
            },
            200)

    @classmethod
    def register_api_endpoint(cls, app):
        """ Register an endpoint to the flask application """
        func = cls.as_view(cls.endpoint)
        app.add_url_rule("%s/" % cls.prefix, defaults={cls.pk["name"]: None},
                view_func=func, methods=["GET"])
        app.add_url_rule("%s/" % cls.prefix,
                view_func=func, methods=["POST"])

class User(Api):
    endpoint = 'user_api'
    prefix = '/users'
    pk = {'name': 'user_id', 'type': 'int'}

    def get(self, user_id):
        results = []

        with session_scope(self.db) as session:
            query = session.query(models.User)

            if user_id is not None:
                query = query.filter_by(id=user_id)

            results = map(lambda el: el.get_json(), query.all())

        if user_id is not None and not results:
            raise NotFound("user %d not found" % user_id)

        return make_json_response({'collection': results}, 200)

    def post(self):
        schema = models.User.get_schema()
        new_user_id = None

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                new_user = models.User(**data)
                session.add(new_user)
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message': "user added"
            },
            200)

    def delete(self, user_id):
        try:
            with session_scope(self.db) as session:
                result = session.query(models.User) \
                    .filter_by(id=user_id) \
                    .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("user %d not found" % user_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message' : "user %d deleted" % user_id
            },
            200)

    def put(self, user_id):
        self.patch(user_id)

    def patch(self, user_id):
        schema = models.User.get_schema()

        try:
            data = schema(request.json)
            with session_scope(self.db) as session:
                result = session.query(models.User) \
                    .filter_by(id=user_id) \
                    .one()
                session.delete(result)
        except NoResultFound:
            raise NotFound("user %d not found" % user_id)
        except IntegrityError, e:
            raise BadRequest(str(e))

        return make_json_response({
            'message' : "user %d updated" % user_id
            },
            200)

apis = [Assignment, Course, Submit, User]
__all__ = map(lambda klazz: klazz.__name__, apis)
