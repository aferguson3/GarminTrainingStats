import logging

from flask import render_template

from backend.server import create_app
from backend.server.config import db, cache, BaseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = create_app(db, cache, app_config=BaseConfig())


@app.route("/")
def hello():
    return "Hello, world!"


@app.errorhandler(404)
def not_found(*args, **kwargs):
    return render_template("not_found.html", msg="Not Found"), 404
