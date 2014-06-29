from database.base import Base
from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref

class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False, unique = True)
    deadline = Column(DateTime, nullable = False)
    statement_url = Column(String)
    upload_active_from = Column(DateTime, nullable = False)
    upload_active_to = Column(DateTime, nullable = False)
    timedelta = Column(Float, nullable = False, default = 0.0)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable = False)
    tester_id = Column(Integer, ForeignKey('testers.id'))
    storer_id = Column(Integer, ForeignKey('storers.id'))

    submits = relationship('Submit', backref = 'assignment')

    def update(self, data):
        for key, value in dict.iteritems(data):
            setattr(self, key, value)

    def to_json(self):
        return {
                'id' : self.id,
                'name' : self.name,
                'deadline' : self.deadline,
                'statement_url' : self.statement_url,
                'upload_active_from' : self.upload_active_from,
                'upload_active_to' : self.upload_active_to,
                'course' : {
                    'id' : self.course.id,
                    'name' : self.course.name
                    },
                'tester_id' : self.tester_id,
                'storer_id' : self.storer_id,
                'submits' : map(
                    lambda submit: {
                        'id' : submit.id,
                        'grade' : submit.grade,
                        'username' : submit.user.username
                        },
                    self.submits)
                }
