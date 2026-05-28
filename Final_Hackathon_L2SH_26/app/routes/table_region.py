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

    data = json.load(open("app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data)[["Место", "Регион", "Итог"]].sort_values("Итог", ascending=False).reset_index(drop=True)
    df["Место"] = df.index + 1
    df["Призёр"] = (df["Место"] <= 225) & (df["Место"] > 40)
    df["Победитель"] = df["Место"] <= 40
    df = df.groupby("Регион").agg(
        Participants = ("Место", "count"),
        Prized = ("Призёр", "sum"),
        Winners = ("Победитель", "sum"),
        MinPlace = ("Место", "min"),
        MaxPlace = ("Место", "max"),
    ).reset_index().sort_values("Participants", ascending=False).reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "Регион", "Participants"]].values.tolist()

    print(rows)

    return render_template("table_region.html", rows=rows)