import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

try:
    connection = open(os.path.join(os.path.dirname(__file__), "DB_CONNECTION")
                 ).readline().strip()
except IOError:
    raise IOError("You must write a DB connection string into the "
                  "DB_CONNECTION file.")
engine = create_engine(connection, convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = session.query_property()

def init_db():
    import model
    model.Base.metadata.create_all(bind=engine)
