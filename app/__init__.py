from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cfg import Config
from flask_login import LoginManager

app = Flask(__name__)

# have to set database uri to initialize database: this should be done in a config file
app.config_from_object(Config)
# we should probably be using this
db = SQLAlchemy(app)
app.config.from_object(Config)

db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'




migrate = Migrate(app, db)

