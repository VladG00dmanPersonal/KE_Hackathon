from flask import Blueprint, render_template
from app.db import get_db
import pandas as pd
import json

bp = Blueprint("table_region", __name__, url_prefix="/table_region")


@bp.route("/")
def index():
    # rows = get_db().execute(
    #     """
    #     SELECT tr.*, u.email AS creator_email
    #     FROM table_rows tr
    #     LEFT JOIN users u ON u.id = tr.created_by
    #     ORDER BY tr.created_at DESC
    #     """
    # ).fetchall()

    data = json.load(open("app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))
    tour1 = []
    tour2 = []

    for k, v in data['Первый тур'].items():
        tour1.extend(v)
    
    for k, v in data['Второй тур'].items():
        tour2.extend(v)

    df = pd.concat([pd.DataFrame(tour1), pd.DataFrame(tour2)], ignore_index=True)
    print(df.head())

    return render_template("table_region.html")