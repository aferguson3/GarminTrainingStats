from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from backend.server.config import db, cache, db_config, BaseConfig
from backend.server.routes import *
from backend.src import client_auth

APP_CONFIG = BaseConfig()


def register_blueprints(app_: Flask):
    app_.register_blueprint(database_bp)
    app_.register_blueprint(service_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(login_bp)
    app_.register_blueprint(statues_bp)


def create_app(db_: SQLAlchemy, cache_: Cache, app_config: BaseConfig | None = None):
    """
    :param db_:
    :param cache_:
    :param app_config: Options: BaseConfig, DebugConfig, or ProdConfig
    :return:
    """
    app_config = BaseConfig() if app_config is None else app_config
    curr_app = Flask(__name__)
    curr_app.config_class = BaseConfig
    curr_app.config.from_object(app_config)

    if curr_app.config["DEBUG"] is True:
        toolbar = DebugToolbarExtension(curr_app)
    cache_.init_app(curr_app)
    db_.init_app(curr_app)

    with curr_app.app_context():
        db_config(db_, curr_app)
    # cache.clear()
    client_auth()
    register_blueprints(curr_app)

    return curr_app


app = create_app(db, cache, app_config=APP_CONFIG)

if __name__ == "__main__":
    create_app(db, cache, app_config=APP_CONFIG)
