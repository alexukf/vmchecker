from database.base import Base
from sqlalchemy import Integer, String
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String, nullable = False, unique = True)

    submits = relationship('Submit', backref = 'user')

    def update(self, data):
        for key, value in dict.iteritems(data):
            setattr(self, key, value)

    def to_json(self):
        return {
                'id' : self.id,
                'username' : self.username
                }
