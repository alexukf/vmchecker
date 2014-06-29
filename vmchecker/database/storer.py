from database.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref

class Storer(Base):
    __tablename__ = 'storers'

    id = Column(Integer, primary_key = True, autoincrement = True)
    hostname = Column(String, nullable = False)
    sshid = Column(String, nullable = False)
    known_hosts_file = Column(String, nullable = False)
