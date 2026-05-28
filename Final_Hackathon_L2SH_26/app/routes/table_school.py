from flask import Blueprint, render_template
from app.db import get_db
import json
import pandas as pd
from app.static.task2.func import get_school

bp = Blueprint("table_school", __name__, url_prefix="/table_school")


@bp.route("/Participants")
def index():
    data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data)[["Участник", "Место", "Регион", "Итог"]].sort_values("Итог", ascending=False).reset_index(drop=True)
    df['school'] = df['Участник'].apply(lambda x: get_school(x)[0])
    df["Место"] = df.index + 1
    df["Призёр"] = (df["Место"] <= 225) & (df["Место"] > 40)
    df["Победитель"] = df["Место"] <= 40
    df = df.dropna()
    df = df.groupby("school").agg(
        Participants = ("Место", "count"),
        Prized = ("Призёр", "sum"),
        Winners = ("Победитель", "sum"),
        MinPlace = ("Место", "min"),
        MaxPlace = ("Место", "max"),
    ).reset_index().sort_values(["Participants", "school"], ascending=[False, True]).reset_index(drop=True)

    df = df[df['Participants'] > 0].reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "school", "Participants"]].values.tolist()

    print(1)

    return render_template("table_school.html", rows=rows, param="Участников")


@bp.route("/Prized")
def index2():
    data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data)[["Участник", "Место", "Регион", "Итог"]].sort_values("Итог", ascending=False).reset_index(drop=True)
    df['school'] = df['Участник'].apply(lambda x: get_school(x)[0])
    df["Место"] = df.index + 1
    df["Призёр"] = (df["Место"] <= 225) & (df["Место"] > 40)
    df["Победитель"] = df["Место"] <= 40
    df = df.dropna()
    df = df.groupby("school").agg(
        Participants = ("Место", "count"),
        Prized = ("Призёр", "sum"),
        Winners = ("Победитель", "sum"),
        MinPlace = ("Место", "min"),
        MaxPlace = ("Место", "max"),
    ).reset_index().sort_values(["Prized", "school"], ascending=[False, True]).reset_index(drop=True)

    df = df[df['Prized'] > 0].reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "school", "Prized"]].values.tolist()

    print(1)

    return render_template("table_school.html", rows=rows, param="Призёров")


@bp.route("/Winners")
def index3():
    data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data)[["Участник", "Место", "Регион", "Итог"]].sort_values("Итог", ascending=False).reset_index(drop=True)
    df['school'] = df['Участник'].apply(lambda x: get_school(x)[0])
    df["Место"] = df.index + 1
    df["Призёр"] = (df["Место"] <= 225) & (df["Место"] > 40)
    df["Победитель"] = df["Место"] <= 40
    df = df.dropna()
    df = df.groupby("school").agg(
        Participants = ("Место", "count"),
        Prized = ("Призёр", "sum"),
        Winners = ("Победитель", "sum"),
        MinPlace = ("Место", "min"),
        MaxPlace = ("Место", "max"),
    ).reset_index().sort_values(["Winners", 'school'], ascending=[False, True]).reset_index(drop=True)

    df = df[df['Winners'] > 0].reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "school", "Winners"]].values.tolist()

    print(1)

    return render_template("table_school.html", rows=rows, param="Победителей")


@bp.route("/Diplomed")
def index4():
    data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data)[["Участник", "Место", "Регион", "Итог"]].sort_values("Итог", ascending=False).reset_index(drop=True)
    df['school'] = df['Участник'].apply(lambda x: get_school(x)[0])
    df["Место"] = df.index + 1
    df["Призёр"] = (df["Место"] <= 225) & (df["Место"] > 40)
    df["Победитель"] = df["Место"] <= 40
    df = df.dropna()
    df = df.groupby("school").agg(
        Participants = ("Место", "count"),
        Prized = ("Призёр", "sum"),
        Winners = ("Победитель", "sum"),
        MinPlace = ("Место", "min"),
        MaxPlace = ("Место", "max"),
    ).reset_index()
    df["Diplomed"] = df["Prized"] + df["Winners"]
    df = df.sort_values(["Diplomed", 'school'], ascending=[False, True]).reset_index(drop=True)
    df = df[df['Diplomed'] > 0].reset_index(drop=True)
    df["Place"] = df.index + 1

    rows = df[["Place", "school", "Diplomed"]].values.tolist()

    print(1)

    return render_template("table_school.html", rows=rows, param="Дипломов")