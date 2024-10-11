import logging
import pathlib

import dotenv
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

BASEDIR = pathlib.Path.cwd()
DB_URI = "sqlite:///" + str(BASEDIR / "data" / "workouts.db")
TEST_URI = "sqlite:///" + str(BASEDIR / "data" / "test_workouts.db")
ENV_PATH = pathlib.Path.cwd().parent.parent / ".env"
logger = logging.getLogger(__name__)

db = SQLAlchemy()
cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_THRESHOLD": 20,
        "CACHE_DEFAULT_TIMEOUT": 250,
    }
)


def db_config(db_, app_):
    try:
        db_.create_all()
        logger.info(f"DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}")
    except OperationalError:
        raise FileNotFoundError(
            f"Unable to open DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}"
        )


def _db_uri_selection(uri_type):
    """
    :param uri_type: Options: IN_MEMORY_DB, TEST_DB, or MAIN_DB
    :type uri_type: str
    :return: Sqlalchemy Database URI
    """

    if isinstance(uri_type, str):

        if str(uri_type.upper()) == "IN_MEMORY_DB":
            selection = "sqlite:///:memory:"
        elif str(uri_type.upper()) == "TEST_DB":
            selection = TEST_URI
        elif str(uri_type.upper()) == "MAIN_DB":
            selection = DB_URI
        else:
            raise RuntimeError(f"Invalid DB URI: {uri_type} was used.")
        return selection
    else:
        logger.debug(f"{uri_type} is not str type")


class BaseConfig(object):

    SECRET_KEY = dotenv.get_key(str(ENV_PATH), "SECRET_KEY")

    def __init__(self, uri_type: str = "MAIN_DB"):
        """
        :param uri_type: Options: IN_MEMORY_DB, TEST_DB, or MAIN_DB
        :type uri_type: str
        """
        self.uri_type = uri_type

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return _db_uri_selection(self.uri_type)


class DebugConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    def __init__(self, uri_type: str = "TEST_DB"):
        super().__init__()
        self.uri_type = uri_type


class ProdConfig(BaseConfig):
    DEBUG = False
