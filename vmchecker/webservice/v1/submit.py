import os
import tempfile
import magic
from api import API
from flask import request, current_app
from database.submit import Submit
from webservice.util import make_json_response
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from database.util import parse_options
from voluptuous import Schema, Required, All, Range, Length, Coerce, MultipleInvalid, Invalid

# this validator saves the files before checking the mime type
def MimeType(mimetypes = []):
    def validate(f):
        m = magic.open(magic.MAGIC_MIME_TYPE)
        m.load()
        # because reading the mime type messes up the file descriptor
        # we save the file here
        (fd, tmpname) = tempfile.mkstemp()
        os.close(fd)
        f.save(tmpname)

        mimetype = m.file(tmpname)
        if mimetype not in mimetypes:
            os.remove(tmpname)
            raise Invalid("invalid mimetype %s" % mimetype)

        setattr(f, 'tmpname', tmpname)
        return f

    return validate

class SubmitAPI(API):
    endpoint = "submit_api"
    prefix = "/submits"
    pk = { 'name' : 'submit_id', 'type' : 'int' }

    def get(self, submit_id):
        query = self.session.query(Submit)

        if submit_id is not None:
            try:
                result = query.filter_by(id = submit_id).one()
                return make_json_response(result, 200)
            except NoResultFound:
                raise NotFound("submit %d was not found" % submit_id)

        query = parse_options(request.args.items(), query)

        result = map(lambda row: row.to_json(), query.all())
        return make_json_response({ "collection" : result }, 200)

    def post(self):
        schema = Schema({
            Required('user_id') : All(Coerce(int), Range(min = 0)),
            Required('assignment_id') : All(Coerce(int), Range(min = 0))
            })

        file_schema = Schema({
            Required('file') : All(
                MimeType(['application/zip']))
            })

        try:
            # validate request form data
            data = schema(request.form.to_dict(flat = True))
            #result = self.session.query(Submit) \
            #        .filter_by(user_id = data['user_id']) \
            #        .order_by(.all()

            files = file_schema(request.files.to_dict(flat = True))
            new_submit = Submit(**data)
            new_submit.filename = files['file'].tmpname
            self.session.add(new_submit)
            self.session.flush()
        except IntegrityError, e:
            raise BadRequest(str(e))
        except MultipleInvalid, e:
            raise BadRequest(str(e))

        #try:
        #    submit.submit(new_submit.filename, new_submit.assignment_id,
        #            new_submit.user.username, new_submit.assignment.course_id)

        self.session.commit()

        return make_json_response({
            "message" : "submit %d added" % new_submit.id,
            "grade" : 95,
            "comments" : "<p>-5p inconsistent indenting</p>"
            },
            200)

    def delete(self, submit_id):
        # TODO we don't support submit deletion
        pass

    def put(self, submit_id):
        # TODO we don't support submit updating
        pass
