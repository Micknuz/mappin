from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from model import *
from db import engine
Base.metadata.create_all(engine)
