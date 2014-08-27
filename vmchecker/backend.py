# -*- coding: utf-8 -*-

import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from .database import models
from .database.models import Base

# TODO move this to a configuration file :)
DATABASE_NAME = '/var/run/vmchecker/db.sqlite'

class Database(object):
    def __init__(self, dbname=None):
        raise NotImplementedError

    def initialize_db(self):
        raise NotImplementedError

    def create_session(self):
        raise NotImplementedError

@contextmanager
def session_scope(db):
    """Provide a transactional scope around a series of operations."""
    session = db.create_session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class SQLiteDb(Database):
    def __init__(self, db_url=None):
        if db_url is not None:
            self.engine = create_engine("sqlite:///%s" % db_url,
                                        echo=True)
        else:
            # this is here for debug purposes
            self.engine = create_engine("sqlite:///:memory:",
                                        echo=True,
                                        connect_args={
                                            'check_same_thread' : False
                                            },
                                        poolclass=StaticPool)
        self.engine.execute('pragma foreign_keys=on')

        session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.Session = scoped_session(session_factory)

    def initialize(self):
        Base.metadata.create_all(self.engine)

        # add the initial user
        with session_scope(self) as session:
            result = session.query(models.User).filter_by(username='admin')
            if not result.first():
                admin = models.User(username='admin',
                                    password=bcrypt.hashpw('123456', bcrypt.gensalt()))
                session.add(admin)

    def create_session(self):
        return self.Session()

__db__ = None
def get_db():
    global __db__
    if __db__ is None:
        __db__ = SQLiteDb(DATABASE_NAME)

    return __db__
