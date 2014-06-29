from datetime import datetime
from flask import request
from webservice.util import make_json_response, Date
from webservice.v1.api import API
from database.util import parse_options
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound
from voluptuous import Schema, Required, All, Range, Length, MultipleInvalid, Coerce
from database.assignment import Assignment

class AssignmentAPI(API):
    endpoint = "assignment_api"
    prefix = "/assignments"
    pk = { 'name' : 'assignment_id', 'type' : 'int' }

    def get(self, assignment_id):
        query = self.session.query(Assignment);

        if assignment_id is not None:
            try:
                result = query.filter_by(id = assignment_id).one()
                return make_json_response(result.to_json(), 200)
            except NoResultFound:
                raise NotFound("assignment %d does not exist" % assignment_id)

        # TODO add support for filtering using request arguments
        query = parse_options(request.args.items(), query)

        result = map(lambda row: row.to_json(),
                query.all())
        return make_json_response(
                { "collection" : result },
                200)

    def post(self):
        schema = Schema({
            Required('name') : All(unicode, Length(min = 1)),
            Required('statement_url') : All(unicode, Length(min = 1)),
            Required('deadline') : All(Date()),
            Required('upload_active_from') : All(Date()),
            Required('upload_active_to') : All(Date()),
            Required('course_id') : All(Coerce(int), Range(min = 0))
            })

        try:
            # validate request form data
            data = schema(request.form.to_dict(flat = True))
            new_assignment = Assignment(**data)
            self.session.add(new_assignment)
            self.session.commit()
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response(
                { "message" : "assignment %d added" % new_assignment.id },
                200)

    def delete(self, assignment_id):
        try:
            result = self.session.query(Assignment).filter_by(id = assignment_id).one()
            session.delete(result)
            session.commit()
        except NoResultFound:
            raise NotFound("Assignment %d does not exist" % assignment_id)
        except IntegrityError:
            raise BadRequest("Failed to commit to database")

        return make_json_response(
                { "message" : "assignment %d deleted" % assignment_id },
                200)

    def put(self, assignment_id):
        schema = Schema({
            Required('name') : All(str, Length(min = 1)),
            Required('deadline') : All(Date()),
            Required('statement_url') : All(Date()),
            Required('upload_active_from') : All(Date()),
            Required('upload_active_to') : All(Date()),
            Required('timedelta') : All(float, Range(min = 0.0)),
            Required('course_id') : All(int, Range(min = 0)),
            Required('tester_id') : All(int, Range(min = 0)),
            Required('storer_id') : All(int, Range(min = 0))
            })

        try:
            result = self.session.query(Assignment).filter_by(id = assignment_id).one()

            # validate request form
            data = schema(**request.form)
            result.update(**data)
            session.commit()
        except NoResultFound:
            raise NotFound("Assignment %d does not exist" % assignment_id)
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response(
                { "message" : "assignment %d updated" % assignment_id },
                200)

    def patch(self, assignment_id):
        schema = Schema({
            'name' : All(str, Length(min = 1)),
            'deadline' : All(Date()),
            'statement_url' : All(str, Length(min = 1)),
            'upload_active_from' : All(Date()),
            'upload_active_to' : All(Date()),
            'timedelta' : All(float, Range(min = 0.0)),
            'course_id' : All(float, Range(min = 0)),
            'tester_id' : All(float, Range(min = 0)),
            'storer_id' : All(float, Range(min = 0))
            })

        try:
            result = self.session.query(Assignment).filter_by(id = assignment_id).one()

            # validate data
            data = schema(**request.form)
            result.update(**data)
            session.commit()
        except NoResultFound:
            raise NotFound("Assignment %d does not exist" % assignment_id)
        except IntegrityError:
            raise BadRequest("Failed to commit to database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        return make_json_response(
                { "message" : "assignment %d updated" % assignment_id },
                200)
