from flask import Blueprint, render_template

statues_bp = Blueprint("statues_bp", __name__, url_prefix="")


@statues_bp.route("/")
def hello():
    return "Hello, world!"


@statues_bp.errorhandler(404)
def not_found(*args, **kwargs):
    return render_template("not_found.html", msg="Not Found"), 404
