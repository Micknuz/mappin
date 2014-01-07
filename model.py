import re
import hashlib
import datetime
from sqlalchemy import schema, orm, Column, ForeignKey, select
from sqlalchemy.sql import func, expression as expr, functions, join
from sqlalchemy.orm import column_property, mapper, relationship, backref
from sqlalchemy.types import *
from flask.ext.wtf import Form, TextField, TextAreaField, validators, DateField

import db

Base = db.Base


class Password(object):

    ENCODING = "utf-8"
    __slots__ = "hash_str"

    @classmethod
    def hash(cls, password):
        if isinstance(password, unicode):
            password = password.encode(cls.ENCODING)
        if not password:
            raise ValueError("password must be filled")
        return hashlib.sha1(password).hexdigest()

    def __init__(self, password_hash):
        self.hash_str = password_hash

    def __eq__(self, password):
        if isinstance(password, type(self)):
            return self.hash_str == password.hash_str
        else:
            return self.hash_str == Password.hash(password)

class Person(Base):

    ID_PATTERN = re.compile(r"^[-a-z0-9_.]{3,}$")

    __tablename__ = "person"

    id = Column(Text, primary_key=True)
    password_hash = Column(String(40), nullable=False)
    privileged = Column(Boolean, default=False)

    @orm.validates("id")
    def validate_id(self, key, id):
        id = id.strip().lower()
        if not id:
            raise ValueError("id must be filled")
        if len(id) < 3:
            raise ValueError("id must be longer than 3 characters")
        if self.ID_PATTERN.match(id):
            return id
        raise ValueError("id is invalid: " + repr(id))

    @property
    def password(self):
        return Password(self.password_hash)

    @password.setter
    def password(self, password):
        self.password_hash = Password.hash(password)


class Mappin(Base):

    __tablename__ = "mappin"
    map_id = Column(Integer, ForeignKey('map.id'), primary_key=True)
    pin_id = Column(Integer, ForeignKey('pin.id'), primary_key=True)
    insert_date = Column(DateTime(timezone=True), default=datetime.datetime.now)
    pin = relationship("Pin", backref="maps")

class Map(Base):

    __tablename__ = "map"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    manager_id = Column("created_by", Text, ForeignKey(Person.id), 
                    nullable=False, index=True)
    privileged = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    pins = relationship("Mappin", backref="map")
    insert_date = Column(DateTime(timezone=True), default=datetime.datetime.now)
    update_date = Column(DateTime(timezone=True), default=datetime.datetime.now)

class Pin(Base):

    __tablename__ = "pin"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    score = Column(Integer, default=0)
    address = Column(String, nullable=True)
    lat = Column(Float)
    lng = Column(Float)
    insert_date = Column(DateTime(timezone=True), default=datetime.datetime.now)


class PinForm(Form):
    name = TextField(u'name', [validators.Required()])
    description = TextAreaField(u'description')
    address = TextField(u'address',  [validators.Required()])
    lat = TextField(u'lat',  [validators.Required()])
    lng = TextField(u'lng',  [validators.Required()])

class Url(Base):

    __tablename__ = "url"

    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    score = Column(Integer, default=0)
    insert_date = Column(DateTime(timezone=True), default=datetime.datetime.now)
    pin_id = Column(Integer, ForeignKey('pin.id'))
    pin = relationship('Pin', backref=backref('urls', order_by=insert_date))

class UrlForm(Form):
    url = TextField(u'URL', [validators.Required()])
    description = TextAreaField(u'description')

class Image(Base):

    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=True)
    insert_date = Column(DateTime(timezone=True), default=datetime.datetime.now)
    pin = relationship('Pin', backref=backref('images', order_by=insert_date))
    pin_id = Column(Integer, ForeignKey('pin.id'), primary_key=True)


"""
class Professor(Base):

    __tablename__ = "professor"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    major_id = Column(Integer, ForeignKey(Major.id), nullable=True)
    major = orm.relationship(Major, backref="professors")
    university_id = Column(Integer, ForeignKey(University.id), nullable=True)
    university = orm.relationship(University, backref="professors")
    point = Column(Integer, default=0)

class Dislike(Base):

    __tablename__ = "vote"
    __table_args__ = (schema.UniqueConstraint("voted_by", "professor_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("voted_by", Text, ForeignKey(Person.id), nullable=False,
                     index=True)
    user = orm.relationship(Person)
    professor_id = Column(Integer, ForeignKey(Professor.id), nullable=False,
                     index=True)
    professor = orm.relationship(Professor)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    comment = Column(Text, default='')

"""
