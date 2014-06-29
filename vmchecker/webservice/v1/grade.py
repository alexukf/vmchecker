from api import API
from database.submit import Submit
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound
from voluptuous import Schema, Required, All, Range, MultipleInvalid, Coerce
from flask import request

class GradeAPI(API):
    endpoint = "grade_api"
    prefix = "/grades"

    def get(self, assignment_id, user_id):
        query = self.session.query(Grade)

        query = query.filter_by(assignment_id = assignment_id)
        query = query.filter_by(user_id = user_id)

        try:
            result = query.filter_by(assignment_id = assignment_id) \
                    .filter_by(user_id = user_id).one()
        except NoResultFound:
            raise NotFound("There is no grade for user %d for assignment %d" %
                    (user_id, assignment_id))

        return make_json_response(result.to_json(), 200)

    def put(self, assignment_id, user_id):
        query = self.session.query(Grade)
        schema = Schema({
            Required('grade') : All(Coerce(float), Range(min = -100.0, max = 200.0))
            })

        try:
            # validate request form data
            data = schema(request.form.to_dict(flat = True))

            try:
                result = query.filter_by(assignment_id = assignment_id) \
                        .filter_by(user_id = user_id).one()
                result.update(data)

                self.session.commit()

                return make_json_response({ "message" : "grade updated" }, 200)
            except NoResultFound:
                new_grade = Grade(**data)
                new_grade.user_id = user_id
                new_grade.assignment_id = assignment_id
                self.session.add(new_grade)

                self.session.commit()

                return make_json_response({ "message" : "grade created" }, 200)
        except IntegrityError:
            raise BadRequest("Failed to commit to the database")
        except MultipleInvalid, e:
            raise BadRequest(str(e))

    @classmethod
    def register_api_endpoint(cls, app):
        func = cls.as_view(cls.endpoint)
        app.add_url_rule("%s/<int:assignment_id>/<int:user_id>" % cls.prefix,
                view_func = func, methods=["GET"])
        app.add_url_rule("%s/<int:assignment_id>/<int:user_id>" % cls.prefix,
                view_func = func, methods=["PUT"])
