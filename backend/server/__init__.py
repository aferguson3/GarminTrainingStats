import logging

from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from backend.server.config import BaseConfig, db_config, DebugConfig
from backend.server.routes import database_bp, service_bp, admin_bp, statues_bp
from backend.src import client_auth

logger = logging.getLogger(__name__)


def create_app(db: SQLAlchemy, cache: Cache, app_config: BaseConfig | None = None):
    app_config = BaseConfig() if app_config is None else app_config
    curr_app = Flask(__name__)
    curr_app.config_class = BaseConfig
    curr_app.config.from_object(app_config)

    if curr_app.config["DEBUG"] is True:
        toolbar = DebugToolbarExtension(curr_app)
    cache.init_app(curr_app)
    db.init_app(curr_app)

    with curr_app.app_context():
        db_config(db, curr_app)
    # cache.clear()
    client_auth()
    register_blueprints(curr_app)

    return curr_app


def register_blueprints(app: Flask):
    app.register_blueprint(database_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(statues_bp)
