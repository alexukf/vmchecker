from database.base import Base
from database.assignment import Assignment
from sqlalchemy import Integer, String
from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False, unique = True)
    repository_path = Column(String, nullable = False, default = '/')
    root_path = Column(String, nullable = False, default = '/')

    assignments = relationship('Assignment',
            order_by = 'Assignment.id',
            backref = 'course')

    def update(self, data):
        for key, value in dict.iteritems(data):
            setattr(self, key, value)

    def to_json(self):
        return {
                'id' : self.id,
                'name' : self.name,
                'repository_path' : self.repository_path,
                'assignments' : map(lambda el: {
                    'id' : el.id,
                    'name' : el.name
                    },
                    self.assignments)
                }



