import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SERVER_NAME = 'localhost:8080'

    if os.path.exists('/debug*'):
        DEBUG = True

    database = os.environ.get('MYSQL_DATABASE')
    user = os.environ.get('MYSQL_USER')
    password = os.environ.get('MYSQL_PASSWORD')
    host = os.environ.get('MYSQL_HOST')
    port = os.environ.get('MYSQL_PORT') or 3306
    os.environ['DATABASE_URL'] = "mysql+pymysql://%s:%s@%s:%d/%s" % (user, password, host, port, database)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
