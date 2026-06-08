import os
import json

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
import pandas as pd
from app.db import get_db
from app.utils import ALLOWED_FILE_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, allowed_file, login_required, unique_filename
from app.static.task2.func import get_school
import numpy as np


bp = Blueprint("results", __name__, url_prefix="/results")


def save_upload(file_storage, subdir, extensions):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename, extensions):
        return False
    filename = unique_filename(file_storage.filename)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subdir)
    file_storage.save(os.path.join(upload_dir, filename))
    return f"uploads/{subdir}/{filename}"


@bp.route("/example", methods=("GET", "POST"))
def example():
    data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
    df = pd.DataFrame(data).sort_values("Итог", ascending=False).reset_index(drop=True)
    df['Школа'] = df['Участник'].apply(lambda x: get_school(x)[0])
    df["Место"] = df.index + 1
    rows = []
    cols = []


    if request.method == "POST":
        tour = request.form.get("option_value2", "basic")
        grade = request.form.get("option_value", "basic")
        region = request.form.get("option_value3", "basic")
        print(tour)

        if tour == 'both':
            data = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))["Второй тур"]["300"]
            df = pd.DataFrame(data).sort_values("Итог", ascending=False).reset_index(drop=True)
            df['Школа'] = df['Участник'].apply(lambda x: get_school(x)[0])
            df["Место"] = df.index + 1

            grade_filter = df['Класс'].astype(int) > 0

            if grade == "all":
                pass
            elif grade == "only_11":
                grade_filter = df['Класс'].astype(int) == 11
            elif grade == "only_10":
                grade_filter = df['Класс'].astype(int) == 10
            elif grade == "only_9":
                grade_filter = df['Класс'].astype(int) == 9
            elif grade == "10_and_lower":
                grade_filter = df['Класс'].astype(int) <= 10
            elif grade == "9_and_lower":
                grade_filter = df['Класс'].astype(int) <= 9
            elif grade == "8_and_lower":
                grade_filter = df['Класс'].astype(int) <= 8
            
            df = df[grade_filter]

            print(tour, grade, region)
            print(df)

    countries = [{id: 1, "name": "Москва"}, {id: 2, "name": "Санкт-Петербург"}, {id: 3, "name": "Республика Татарстан"}, {id: 4, "name": "Московская область"}, {id: 4, "name": "Новосибирская область"}, {id: 5, "name": "Челябинская область"}, {id: 6, "name": "Свердловская область"}, {id: 7, "name": "Пермский край"}, {id: 8, "name": "Новосибирская область"}, {id: 9, "name": "Липецкая область"}, {id: 10, "name": "Оренбургская область"}, {id: 11, "name": "Республика Башкортостан"}]
    file = open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/schools_moscow.txt", "r", encoding="utf-8")
    schools_moscow = [{id: i, "name": line.strip()} for i, line in enumerate(file.readlines(), start=1)]
    file.close()
    file = open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/schools_spb.txt", "r", encoding="utf-8")
    schools_spb = [{id: i, "name": line.strip()} for i, line in enumerate(file.readlines(), start=1)]
    file.close()
    print(schools_moscow)
    print(schools_spb)
    return render_template("results/example.html", tags=countries, filters={}, schools_moscow=schools_moscow, schools_spb=schools_spb)

