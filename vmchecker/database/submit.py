from database.base import Base
from sqlalchemy import Integer
from sqlalchemy import Column, ForeignKey, Float, DateTime, String
from datetime import datetime

class Submit(Base):
    __tablename__ = 'submits'

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    assignment_id = Column(Integer, ForeignKey('assignments.id'))

    grade = Column(Float, nullable = True)
    filename = Column(String, nullable = False)
    upload_time = Column(DateTime, nullable = False, default = datetime.utcnow)
    comments = Column(String, nullable = True)

    def update(self, data):
        for key, value in dict.iteritems(data):
            setattr(self, key, value)

    def to_json(self):
        return {
                'user' : {
                    'id' : self.user.id,
                    'username' : self.user.username
                    },
                'assignment' : {
                    'id' : self.assignment.id,
                    'name' : self.assignment.name
                    },
                'grade' : self.grade,
                'filename' : self.filename,
                'upload_time' : self.upload_time,
                'comments' : self.comments
                }
