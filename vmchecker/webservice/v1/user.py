from api import API
from ..db import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String, nullable = False, unique = True)

    grades = relationship('Grade', backref = 'user')

class UserAPI(API):
    def get(self, user_id):
        session = get_session()
        query = session.query(User)

        for arg, value in request.args.items():
            if arg in Assignment.__table__.columns:
                query = query.filter_by(**{ arg : value })
            elif arg == 'offset':
                query = query.offset(value)
            elif arg == 'limit':
                query = query.limit(value)
            else:
                raise BadRequest("argument %s not recongnized" % arg)

        if user_id is not None:
            result = query.filter_by(id = user_id).all()
            if len(result) == 0:
                raise NotFound("user %d not found" % user_id)

            return make_json_response(result[0].to_json(), 200)

        result = query.all()
        return make_json_response(map(lambda user: user.to_json(), result), 200)

