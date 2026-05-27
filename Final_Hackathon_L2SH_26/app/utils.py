from functools import wraps
import re
from uuid import uuid4

from flask import flash, g, redirect, url_for
from werkzeug.utils import secure_filename


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_FILE_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf", "doc", "docx", "txt", "csv", "xlsx"}
NICKNAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё0-9._-]{3,32}$")


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Войдите в аккаунт, чтобы открыть эту страницу.", "warning")
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("Войдите в аккаунт, чтобы открыть эту страницу.", "warning")
                return redirect(url_for("auth.login"))
            if g.user["role"] not in roles:
                flash("Недостаточно прав для этого действия.", "danger")
                return redirect(url_for("main.index"))
            return view(**kwargs)

        return wrapped_view

    return decorator


def allowed_file(filename, extensions=ALLOWED_FILE_EXTENSIONS):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions


def unique_filename(filename):
    safe_name = secure_filename(filename)
    if "." not in safe_name:
        return f"{uuid4().hex}_{safe_name}"
    stem, extension = safe_name.rsplit(".", 1)
    return f"{stem}_{uuid4().hex}.{extension.lower()}"


def validate_nickname(nickname):
    if not nickname:
        return "Введите никнейм."
    if not NICKNAME_PATTERN.fullmatch(nickname):
        return "Никнейм: 3-32 символа, без пробелов. Разрешены буквы, цифры, точка, подчёркивание и дефис."
    return None


def nickname_is_taken(db, nickname, current_user_id=None):
    rows = db.execute("SELECT id, nickname FROM users").fetchall()
    normalized = nickname.casefold()
    for row in rows:
        if current_user_id is not None and row["id"] == current_user_id:
            continue
        if row["nickname"].casefold() == normalized:
            return True
    return False
