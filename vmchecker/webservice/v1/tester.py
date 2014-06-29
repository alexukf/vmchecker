from api import API
from ..db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

class Tester(Base):
    __tablename__ = 'testers'

    id = Column(Integer, primary_key = True, autoincrement = True)
    login_username = Column(String, nullable = False)
    hostname = Column(String, nullable = False)
    queue_path = Column(String, nullable = False)

    discriminator = Column('type', String)
    __mapper_args__ = { 'polymorphic_on' : discriminator }

    assignments = relationship('Assignment',
            order_by = 'Assignment.id',
            backref = 'tester')

    def to_json(self):
        pass

class VMWareTester(Tester):
    __tablename__ = 'vmwareservers'
    __mapper_args__ = { 'polymorphic_identity' : 'vmwareserver' }

    id = Column(Integer, ForeignKey('testers.id'), primary_key = True)
    type = Column(Integer, nullable = False)
    url = Column(String, nullable = False)
    port = Column(String, nullable = False)
    username = Column(String, nullable = False)
    password = Column(String, nullable = False)
    datastore_name = Column(String, nullable = False)
    datastore_path = Column(String, nullable = False)


