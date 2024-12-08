from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from csi3335f2024 import Config
from flask_login import LoginManager
from datetime import timedelta

app = Flask(__name__)
# have to set database uri to initialize database: this should be done in a config file
# we should probably be using this
app.config.from_object(Config)
db = SQLAlchemy(app)

# app.permanent_session_lifetime = timedelta(minutes=30)

login = LoginManager(app)
login.login_message = None
login.login_view = 'login'

from app.models import Users

from app import routes
