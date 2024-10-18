from flask import Blueprint, render_template

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")


@login_bp.route("/mfa_code", methods=["GET", "POST"])
def get_mfa_code():
    return render_template("mfa_code.html")
