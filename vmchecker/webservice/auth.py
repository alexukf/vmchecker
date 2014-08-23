# -*- coding: utf-8 -*-

import ldap
import bcrypt
from functools import wraps
from flask import g, request
from sqlalchemy.orm.exc import NoResultFound

from ..database import models
from .. import backend
from .exceptions import *
from ..backend import session_scope

def check_ldap_auth(username, password):
    """Try to authenticate using the global LDAP configuration file.

    Return True if authentication succeeded
    """
    ldap_cfg = LdapConfig()
    con = ldap.initialize(ldap_cfg.server())
    con.simple_bind_s(ldap_cfg.bind_user(),
                      ldap_cfg.bind_pass())

    baseDN = ldap_cfg.root_search()
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None

    # XXX : Needs sanitation
    searchFilter = '(uid=' + username + ')'

    timeout = 0
    count = 0

    # find the user's dn
    result_id = con.search(baseDN,
                           searchScope,
                           searchFilter,
                           retrieveAttributes)
    result_set = []
    while 1:
        result_type, result_data = con.result(result_id, timeout)
        if (result_data == []):
            break
        else:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)

    if len(result_set) == 0:
        #no results
        return False

    if len(result_set) > 1:
        # too many results for the same uid
        return False

    user_dn, entry = result_set[0][0]
    con.unbind_s()

    # check the password
    try:
        con = ldap.initialize(ldap_cfg.server())
        con.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        return False

    return True

#alternative_auths = {'ldap': check_ldap_auth}
alternative_auths = {}
def check_auth(username, password):
    user = None
    with session_scope(backend.get_db()) as session:
        try:
            user = session.query(models.User) \
                          .filter_by(username = username) \
                          .one()

            # check if hash is the same
            if bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
                return user
            else:
                user = None
        except NoResultFound:
            pass

        # try other auth methods
        for type, auth in alternative_auths.iteritems():
            if auth(username, password):
                if user is not None:
                    user.password = bcrypt.hashpw(password, bcrypt.gensalt())
                    assert user.auth_type == type
                else:
                    user = models.User(username=username,
                                       password=bcrypt.hashpw(password, bcrypt.gensalt()),
                                       auth_type=type)
                    session.add(user)

    return user

def require_basic_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.authorization
        if not auth:
            raise Unauthorized()
        user = check_auth(auth.username, auth.password)
        if user is None:
            raise Forbidden()
        g.user = user
        return f(*args, **kwargs)
    return decorator
