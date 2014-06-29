from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from database.base import Base

def parse_options(args, query):
    for arg, value in args:
        if arg == 'offset':
            query = query.offset(value)
        elif arg == 'limit':
            query = query.limit(value)

    return query

def create_sqlite_db(db_url = None):
    if not db_url is None:
        engine = create_engine('sqlite:///%s' % (db_url), echo = True)
    else:
        engine = create_engine('sqlite:///:memory:',
                echo = True,
                connect_args = { 'check_same_thread' : False },
                poolclass = StaticPool
                )
        Base.metadata.create_all(engine)

    engine.execute('pragma foreign_keys=on')
    return engine
