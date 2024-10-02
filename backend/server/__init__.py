import logging

from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from backend.server.config import ProdConfig, BaseConfig

logger = logging.getLogger(__name__)


def create_app(app_config: BaseConfig = None):
    app_config = BaseConfig() if app_config is None else app_config

    curr_app = Flask(__name__)
    curr_app.config_class = BaseConfig
    curr_app.config.from_object(app_config)

    toolbar = DebugToolbarExtension(curr_app)
    curr_db = SQLAlchemy(curr_app)
    curr_cache = Cache(curr_app)
    return curr_app, curr_cache, curr_db


app, cache, db = create_app(app_config=ProdConfig())
