from flask import Flask, render_template
from config import Config
import pymysql

# Database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Setup application
app = Flask(__name__)
app.config.from_object(Config)

# Setup database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models