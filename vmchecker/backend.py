# -*- coding: UTF-8 -*-

from .database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

# TODO move this to a configuration file :)
DATABASE_NAME = 'db.sqlite'

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

        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def initialize_db(self):
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()

__db__ = None
def get_db():
    global __db__
    if __db__ is None:
        __db__ = SQLiteDb(DATABASE_NAME)

    return __db__