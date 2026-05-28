import os
import json

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import ALLOWED_FILE_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, allowed_file, login_required, unique_filename


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
# @login_required
def example():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        number_value = request.form.get("number_value", 0, type=float)
        slider_value = request.form.get("slider_value", 50, type=int)
        option_value = request.form.get("option_value", "basic")
        checkbox_values = request.form.getlist("checkbox_values")
        notes = request.form.get("notes", "").strip()
        image_path = save_upload(request.files.get("image"), "forms", ALLOWED_IMAGE_EXTENSIONS)
        file_path = save_upload(request.files.get("file"), "forms", ALLOWED_FILE_EXTENSIONS)

        print(title, number_value, slider_value, option_value)

    countries = [{id: 1, "name": "Москва"}, {id: 2, "name": "Санкт-Петербург"}, {id: 3, "name": "Республика Татарстан"}, {id: 4, "name": "Московская область"}, {id: 4, "name": "Новосибирская область"}, {id: 5, "name": "Челябинская область"}, {id: 6, "name": "Свердловская область"}, {id: 7, "name": "Пермский край"}, {id: 8, "name": "Новосибирская область"}, {id: 9, "name": "Липецкая область"}, {id: 10, "name": "Оренбургская область"}, {id: 11, "name": "Республика Башкортостан"}]

    submissions = get_db().execute(
        """
        SELECT fs.*, u.email AS user_email
        FROM form_submissions fs
        LEFT JOIN users u ON u.id = fs.user_id
        ORDER BY fs.created_at DESC
        LIMIT 10
        """
    ).fetchall()
    return render_template("results/example.html", submissions=submissions, tags=countries, filters={})

