import pathlib

import dotenv
from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

IN_MEMORY = False
TEST_DB = True
DEBUG = True
BASEDIR = pathlib.Path.cwd()
DB_URI = "sqlite:///" + str(BASEDIR / "data" / "workouts.db")
TEST_URI = "sqlite:///" + str(BASEDIR / "data" / "test_workouts.db")

# Flask-SQLite
app = Flask(__name__)
env_path = pathlib.Path.cwd().parent.parent / ".env"
app.config["SECRET_KEY"] = dotenv.get_key(str(env_path), "SECRET_KEY")

if IN_MEMORY:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
elif TEST_DB:
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_URI
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI

# Flask Cache
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_THRESHOLD": 20,
    "CACHE_DEFAULT_TIMEOUT": 250,
}
app.config.from_mapping(cache_config)

# Flask-Toolbar Debugger
if DEBUG is True:
    app.debug = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    toolbar = DebugToolbarExtension(app)

cache = Cache(app)
db = SQLAlchemy(app)
