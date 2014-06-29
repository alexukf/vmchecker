from api import API
from flask import request
from auth import require_roles, require_basic_auth
from webservice.util import make_json_response
from database.util import parse_options
from database.course import Course
from voluptuous import Schema, Required, Length, All
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from voluptuous import MultipleInvalid
from werkzeug.exceptions import BadRequest, NotFound

class CourseAPI(API):
    endpoint = "course_api"
    prefix = "/courses"
    pk = { 'name' : 'course_id', 'type' : 'int' }

    def get(self, course_id):
        query = self.session.query(Course)

        if course_id is not None:
            try:
                result = query.filter_by(id = course_id).one()
                return make_json_response(result.json, 200)
            except NoResultFound:
                raise NotFound("course %d not found" % course_id)

        query = parse_options(request.args.items(), query)

        results = map(lambda row: row.to_json(),
                query.all())
        return make_json_response({ 'collection' : results }, 200)

    def post(self):
        schema = Schema({
            Required('name') : All(unicode, Length(min = 1)),
            Required('repository_path') : All(unicode, Length(min = 1)),
            Required('root_path') : All(unicode, Length(min = 1))
            })

        try:
            # validate request form data
            data = schema(request.form.to_dict(flat = True))
            new_course = Course(**data)
            self.session.add(new_course)
            self.session.commit()
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response(
                { "message" : "course %d added" % new_course.id },
                200)

    def put(self, course_id):
        if course_id is None:
            raise BadRequest("course_id is required")

        schema = Schema({
            Required('name') : All(unicode, Length(min = 1)),
            Required('repository_path') : All(unicode, Length(min = 1)),
            Required('root_path') : All(unicode, Length(min = 1))
            })

        try:
            result = self.session.query(Course).filter_by(id = course_id).one()

            # validate request form data
            data = schema(request.form.to_dict(flat = True))
            result.update(data)
            self.session.commit()
        except NoResultFound:
            raise NotFound("course %d was not found" % course_id)
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response(
                { "message" : "course %d updated" % course_id },
                200)

    def patch(self, course_id):
        if course_id is None:
            raise BadRequest("course_id is required")

        schema = Schema({
            'name' : All(str, Length(min = 1)),
            'repository_path' : All(str, Length(min = 1)),
            'root_path' : All(str, Length(min = 1))
            })

        try:
            result = self.query(Course).filter_by(id = course_id).one()

            # validate request form data
            data = schema(request.form.to_dict(flat = True))
            result.update(data)
            self.session.commit()
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

