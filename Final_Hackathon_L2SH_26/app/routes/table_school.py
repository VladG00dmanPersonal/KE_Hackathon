from flask import Blueprint, render_template
from app.db import get_db
import json

bp = Blueprint("table_school", __name__, url_prefix="/table_school")


@bp.route("/")
def index():
    return render_template("table_school.html")