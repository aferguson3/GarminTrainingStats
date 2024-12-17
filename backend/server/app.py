from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from backend.server.config.config import app_config_selection, db, cache, db_config
from backend.server.routes import *
from backend.server.routes.status_codes import page_not_found


def register_blueprints(app_: Flask):
    app_.register_blueprint(database_bp)
    app_.register_blueprint(service_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(login_bp)
    app_.register_blueprint(statues_bp)


def create_app(
    db_: SQLAlchemy = db, cache_: Cache = cache, app_config: str | None = None, **kwargs
) -> Flask:
    """
    :param db_:
    :param cache_:
    :param app_config: Defines the config type of the Flask environment. Options: base, debug, prod, and test.  Defaults to ``base``
    :return: ``Flask`` instance
    """

    _app_config = app_config_selection(app_config, **kwargs)
    curr_app = Flask(__name__)
    curr_app.config.from_object(_app_config)

    if curr_app.config["DEBUG"] is True:
        DebugToolbarExtension(curr_app)
    cache_.init_app(curr_app)
    db_.init_app(curr_app)

    with curr_app.app_context():
        db_config(db_, curr_app)
    register_blueprints(curr_app)
    curr_app.register_error_handler(404, page_not_found)

    return curr_app


if __name__ == "__main__":
    app = create_app(db, cache, uri_type="TEST_DB", app_config="debug")
    app.run(debug=True)
