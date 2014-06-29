from submit import SubmitAPI
from course import CourseAPI
from assignment import AssignmentAPI
from grade import GradeAPI
from flask import Blueprint
from database.user import User
from database.storer import Storer
from database.tester import Tester

apis = [ SubmitAPI, CourseAPI, AssignmentAPI, GradeAPI ]

def register_blueprint(app):
    api_blueprint = Blueprint('v1', __name__, url_prefix = '/v1')

    for api in apis:
        api.register_api_endpoint(api_blueprint)

    app.register_blueprint(api_blueprint)

