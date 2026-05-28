from flask import Blueprint, render_template
from app.db import get_db
import pandas as pd
import json

bp = Blueprint("table_region", __name__, url_prefix="/table_region")


@bp.route("/Participants")
def index():
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

    print(1)

    return render_template("table_region.html", rows=rows, param="Участников")

@bp.route("/Prized")
def index2():
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
    ).reset_index().sort_values("Prized", ascending=False).reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "Регион", "Prized"]].values.tolist()

    print(2)

    return render_template("table_region.html", rows=rows, param="Призёров")

@bp.route("/Winners")
def index3():
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
    ).reset_index().sort_values("Winners", ascending=False).reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "Регион", "Winners"]].values.tolist()

    print(2)

    return render_template("table_region.html", rows=rows, param="Победителей")

@bp.route("/Diplomas")
def index4():
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
    ).reset_index().sort_values("Winners", ascending=False).reset_index(drop=True)
    df["Diplomed"] = df["Prized"] + df["Winners"]
    df = df.sort_values("Diplomed", ascending=False).reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "Регион", "Diplomed"]].values.tolist()

    print(2)

    return render_template("table_region.html", rows=rows, param="Дипломов")
