from flask import Blueprint, render_template

bp = Blueprint("advertisements", __name__, url_prefix="/advertisements")


@bp.route("/")
def index():
    return render_template("advertisements.html")