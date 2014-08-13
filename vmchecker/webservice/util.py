import os
import tempfile
import magic
from flask import g, jsonify
from datetime import datetime

def teardown_session(exception):
    session = getattr(g, '_session', None)
    if session is not None:
        session.close()

def make_json_response(message, status_code, headers=None):
    response = jsonify(message)
    response.status_code = status_code
    response.headers = headers
    return response

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
        setattr(f, 'mimetype', mimetype)

        return f

    return validate
