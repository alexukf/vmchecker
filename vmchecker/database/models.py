# -*- coding: utf-8 -*-

from .mixins import ApiResource, ApiResourceMeta
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from voluptuous import Schema

__all__ = [
    'Assignment', 'Course', 'Holiday', 'Machine', 'VMwareMachine',
    'Storer', 'Submit', 'Tester', 'VMwareTester', 'User'
    ]

Base = declarative_base(cls=ApiResource, metaclass=ApiResourceMeta)

class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    deadline = Column(DateTime, nullable=False)
    statement_url = Column(String, nullable=False)
    upload_active_from = Column(DateTime, nullable=False)
    upload_active_to = Column(DateTime, nullable=False)
    timedelta = Column(Float, nullable=False, default=180.0)
    penalty_weight = Column(Float, nullable=False)
    total_points = Column(Float, nullable=False)
    timeout = Column(Float, nullable=False)
    storage_type = Column(String, nullable=False, default='normal')

    # foreign keys
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    storer_id = Column(Integer, ForeignKey('storers.id'))

    # back references
    submits = relationship('Submit', backref='assignment')


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    repository_path = Column(String, nullable=False, default='/')
    root_path = Column(String, nullable=False, default='/')

    # back references
    assignments = relationship('Assignment',
                               order_by='Assignment.id',
                               backref='course')


class Holiday(Base):
    __tablename__ = 'holidays'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)


class Machine(Base):
    __tablename__ = 'machines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String, nullable=False)
    vmx_path = Column(String, nullable=False)
    guest_user = Column(String, nullable=False)
    guest_password = Column(String, nullable=False)
    guest_base_path = Column(String, nullable=False)
    guest_shell_path = Column(String, nullable=False)
    guest_home_in_shell = Column(String, nullable=False)
    guest_build_script = Column(String)
    guest_run_script = Column(String)

    # foreign keys
    tester_id = Column(Integer, ForeignKey('testers.id'))

    # back references
    assignments = relationship(Assignment, backref='machine')

    discriminator = Column('type', String, nullable=False, default='vmware')
    __mapper_args__ = {'polymorphic_on' : discriminator}

class VMwareMachine(Machine):
    __tablename__ = 'vmwaremachines'
    __mapper_args__ = {'polymorphic_identity' : 'vmware'}

    id = Column(Integer, ForeignKey('machines.id'), primary_key=True)


class Storer(Base):
    __tablename__ = 'storers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    results_dest = Column(String, nullable=False)
    sshid = Column(String, nullable=False)
    known_hosts_file = Column(String, nullable=False)


class Submit(Base):
    __tablename__ = 'submits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    grade = Column(Float, nullable=True)
    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    comments = Column(String, nullable=True)

    # foreign keys
    user_id = Column(Integer, ForeignKey('users.id'))
    assignment_id = Column(Integer, ForeignKey('assignments.id'))


class Tester(Base):
    __tablename__ = 'testers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login_username = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    queue_path = Column(String, nullable=False)

    # back references
    machines = relationship('Machine', backref='tester')

    discriminator = Column('type', String)
    __mapper_args__ = {'polymorphic_on' : discriminator}

class VMwareTester(Tester):
    __tablename__ = 'vmwaretesters'
    __mapper_args__ = {'polymorphic_identity' : 'vmwareserver'}

    id = Column(Integer, ForeignKey('testers.id'), primary_key=True)
    type = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    port = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    datastore_name = Column(String, nullable=False)
    datastore_path = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # back references
    submits = relationship('Submit', backref='user')
