# Database

from peewee import *
from playhouse.db_url import connect
import os
import logging


# logging.debug('Setting up database connection')
# host = 'db'
# database = os.environ.get('MYSQL_DATABASE')
# user = os.environ.get('MYSQL_USER')
# password = os.environ.get('MYSQL_PASSWORD')
# port = os.environ.get('MYSQL_PORT') or 3306
# logging.debug('mysql:///%s:%s@%s:%d/%s', user, password, host, port, database)
db = connect("mysql://bftp:bftp@db:3306/bftp")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField()
    firstname = CharField(null=False)
    lastname = CharField(null=False)
    username = CharField(null=False)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP NOT NULL')])
    modified = DateTimeField(constraints=[SQL('NULL ON UPDATE CURRENT_TIMESTAMP')])


class Image(BaseModel):
    id = PrimaryKeyField()
    path = CharField(unique=False)
    name = CharField(unique=False)
    size = BigIntegerField(null=False)
    created = DateTimeField(null=False)
    modified = DateTimeField(null=False)
    hash =  CharField(unique=False, index=True)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP NOT NULL')])
    modified = DateTimeField(constraints=[SQL('NULL ON UPDATE CURRENT_TIMESTAMP')])


class ROI(BaseModel):
    id = PrimaryKeyField()
    image = ForeignKeyField(Image, related_name='images')
    top = SmallIntegerField()
    left = SmallIntegerField()
    bottom = SmallIntegerField()
    right = SmallIntegerField()
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP NOT NULL')])
    modified = DateTimeField(constraints=[SQL('NULL ON UPDATE CURRENT_TIMESTAMP')])

    class Meta:
        indexes = (
            (('top', 'left', 'bottom', 'right'), False),
            (('image', 'top', 'left', 'bottom', 'right'), True),
        )


class Object(BaseModel):
    id = PrimaryKeyField()
    roi = ForeignKeyField(ROI, related_name='rois')
    hash = CharField()
    path = CharField()
    userid = ForeignKeyField(User, related_name='user', null=True)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP NOT NULL')])
    modified = DateTimeField(constraints=[SQL('NULL ON UPDATE CURRENT_TIMESTAMP')])


def create_my_tables():
    db.connect()
    db.create_tables([User, Image, ROI, Object], safe=True)