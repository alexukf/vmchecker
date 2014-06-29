from webservice.util import make_json_response
from functools import wraps
from flask import request, g

def check_auth(username, password):
    if username == 'adila' and password == '1234':
        return True
    return False

def get_current_user_role():
    if not 'username' in g:
        return 'guest'

    if g.username == 'adila':
        return 'admin'
    else:
        return 'user'

def require_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles:
                return make_json_response(
                        { 'message': "You don't have access to this resource" },
                        403,
                        {})
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def require_basic_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return make_json_response(
                    'You need to login to access this resource',
                    401,
                    {
                        'WWW-Authenticate' : 'Basic realm = "Login requested"'
                    })
        g.username = auth.username
        g.password = auth.password
        return f(*args, **kwargs)
    return decorator
