from sqlalchemy.sql import text, quoted_name
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# want to unify all of this

# Modify for your own database connection/account
cfg = {"host" : "localhost", "user": "nicholasnolen", "password" : "", "db" : "MariaDeadbeats"}
engineStr = "mysql+pymysql://" + cfg.get("user") + ":" + cfg.get("password") + "@" + cfg.get(
        "host") + ":3306/" + cfg.get("db")

# configuration for database can config from class config to simplify configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DATABASE_URL = os.environ.get('DATABASE_URL') or "mysql+pymysql://nicholasnolen:@localhost/MariaDeadbeats"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL