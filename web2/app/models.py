# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, SmallInteger, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app import db

import os

Base = db.Model
metadata = Base.metadata


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    size = Column(BigInteger, nullable=False)
    hash = Column(String(255), nullable=False, index=True)
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified = Column(DateTime)
    rois = db.relationship('Roi', lazy='select',
        backref=db.backref('image', lazy='joined'))
    rois = db.relationship("Roi", back_populates="image", lazy="dynamic")

    def relative_path(self):
        return os.path.join(self.path, self.name).replace('/var/bftp/', '')


class Object(Base):
    __tablename__ = 'object'

    id = Column(Integer, primary_key=True)
    roi_id = Column(ForeignKey(u'roi.id'), nullable=False, index=True)
    hash = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    userid_id = Column(ForeignKey(u'user.user_id'), index=True)
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified = Column(DateTime)

    roi = relationship(u'Roi')
    userid = relationship(u'User')


class Queue(Base):
    __tablename__ = 'queue'

    id = Column(Integer, primary_key=True)
    image_id = Column(ForeignKey(u'image.id'), nullable=False, index=True)
    priority = Column(SmallInteger)
    status = Column(SmallInteger)

    image = relationship(u'Image')


class Roi(Base):
    __tablename__ = 'roi'
    __table_args__ = (
        Index('roi_top_left_bottom_right', 'top', 'left', 'bottom', 'right'),
        Index('roi_image_id_top_left_bottom_right', 'image_id', 'top', 'left', 'bottom', 'right', unique=True)
    )

    id = Column(Integer, primary_key=True)
    image_id = Column(ForeignKey(u'image.id'), nullable=False, index=True)
    top = Column(SmallInteger, nullable=False)
    left = Column(SmallInteger, nullable=False)
    bottom = Column(SmallInteger, nullable=False)
    right = Column(SmallInteger, nullable=False)
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified = Column(DateTime)

    image = relationship(u'Image')


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified = Column(DateTime)
