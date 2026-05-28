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
        # title = request.form.get("title", "").strip()
        # number_value = request.form.get("number_value", 0, type=float)
        # slider_value = request.form.get("slider_value", 50, type=int)
        # option_value = request.form.get("option_value", "basic")
        # checkbox_values = request.form.getlist("checkbox_values")
        # notes = request.form.get("notes", "").strip()
        # image_path = save_upload(request.files.get("image"), "results", ALLOWED_IMAGE_EXTENSIONS)
        # file_path = save_upload(request.files.get("file"), "results", ALLOWED_FILE_EXTENSIONS)
        option_value = request.form.get("option_value", "all")
        checkbox_values = request.form.getlist("checkbox_values")
        # if not title:
        #     flash("Введите текстовое название.", "danger")
        # elif image_path is False:
        #     flash("Изображение должно быть png, jpg, jpeg, gif или webp.", "danger")
        # elif file_path is False:
        #     flash("Файл имеет неподдерживаемый формат.", "danger")
        # else:
        #     db = get_db()
        #     db.execute(
        #         """
        #         INSERT INTO form_submissions (
        #             user_id,
        #             title,
        #             number_value,
        #             slider_value,
        #             option_value,
        #             checkbox_values,
        #             image_path,
        #             file_path,
        #             notes
        #         )
        #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        #         """,
        #         (
        #             g.user["id"],
        #             title,
        #             number_value,
        #             slider_value,
        #             option_value,
        #             json.dumps(checkbox_values, ensure_ascii=False),
        #             image_path,
        #             file_path,
        #             notes,
        #         ),
        #     )
        #     db.commit()
        #     flash("Форма отправлена и сохранена в SQLite.", "success")
        #     return redirect(url_for("results.example"))

    # submissions = get_db().execute(
    #     """
    #     SELECT fs.*, u.email AS user_email
    #     FROM form_submissions fs
    #     LEFT JOIN users u ON u.id = fs.user_id
    #     ORDER BY fs.created_at DESC
    #     LIMIT 10
    #     """
    # ).fetchall()
    # print(option_value)
    return render_template("results/example.html")

