import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_location = "sqlite:///" + os.path.join(basedir, "app.db")

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or default_db_location
    SECRET_KEY = os.environ.get("SECRET_KEY")
    REMEMBER_COOKIE_DURATION = timedelta(days=7)