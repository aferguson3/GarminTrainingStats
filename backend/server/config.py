import logging
import pathlib

import dotenv
from flask import Flask

BASEDIR = pathlib.Path.cwd()
DB_URI = "sqlite:///" + str(BASEDIR / "data" / "workouts.db")
TEST_URI = "sqlite:///" + str(BASEDIR / "data" / "test_workouts.db")
ENV_PATH = pathlib.Path.cwd().parent.parent / ".env"
logger = logging.getLogger(__name__)


# Choice between IN_MEMORY_DB, TEST_DB, or MAIN_DB
def db_uri_selection(app: Flask, uri_type: str):
    if isinstance(uri_type, str):

        if str(uri_type.upper()) == "IN_MEMORY_DB":
            app.config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        elif str(uri_type.upper()) == "TEST_DB":
            app.config.SQLALCHEMY_DATABASE_URI = TEST_URI
        elif str(uri_type.upper()) == "MAIN_DB":
            app.config.SQLALCHEMY_DATABASE_URI = DB_URI
        else:
            raise RuntimeError(f"Invalid DB URI: {uri_type} was used.")
    else:
        logger.debug(f"{uri_type} is not str type")

    return app


class BaseConfig(object):
    # Flask Cache
    CACHE_TYPE = "SimpleCache"
    CACHE_THRESHOLD = 20
    CACHE_DEFAULT_TIMEOUT = 250
    SECRET_KEY = dotenv.get_key(str(ENV_PATH), "SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = DB_URI

    # TODO: Enable changing of the default DB URI
    def change_db_uri(self, uri_type=None):
        if uri_type is not None:
            SQLALCHEMY_DATABASE_URI = db_uri_selection(uri_type)


class DebugConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = TEST_URI


class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = DB_URI
