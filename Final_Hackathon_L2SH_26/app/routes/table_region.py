from flask import Blueprint, render_template

bp = Blueprint("table_region", __name__, url_prefix="/table_region")


@bp.route("/")
def index():
    return render_template("table_region.html")