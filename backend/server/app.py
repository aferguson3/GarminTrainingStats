import logging

from flask import render_template
from sqlalchemy.exc import OperationalError

from backend.server import db, app
from backend.server.routes.admin import admin_bp
from backend.server.routes.database import database_bp
from backend.server.routes.service import service_bp
from backend.src import client_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def register_blueprints():
    app.register_blueprint(database_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(admin_bp)


@app.route("/")
def hello():
    return "Hello, world!"


@app.errorhandler(404)
def not_found(*args, **kwargs):
    return render_template("not_found.html", msg="Not Found"), 404


def main():
    with app.app_context():
        init_db(db_=db, app_=app)
        # cache.clear()
    client_auth()
    register_blueprints()


def init_db(db_, app_):
    try:
        db_.create_all()
        logger.info(f"DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}")
    except OperationalError:
        raise FileNotFoundError(
            f"Unable to open DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}"
        )


if __name__ == "__main__":
    main()
    app.run()
