import os

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.utils import (
    ALLOWED_IMAGE_EXTENSIONS,
    allowed_file,
    login_required,
    nickname_is_taken,
    unique_filename,
    validate_nickname,
)


bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/")
@login_required
def index():
    db = get_db()
    topups = db.execute(
        """
        SELECT amount, receipt_path, status, admin_comment, created_at, reviewed_at
        FROM topup_requests
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()
    orders = db.execute(
        """
        SELECT id, total, status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("profile.html", topups=topups, orders=orders)


@bp.post("/topup")
@login_required
def create_topup():
    amount = request.form.get("amount", type=float)
    receipt = request.files.get("receipt")

    if amount is None or amount <= 0:
        flash("Введите положительную сумму пополнения.", "danger")
        return redirect(url_for("profile.index"))
    if not receipt or receipt.filename == "":
        flash("Загрузите изображение подтверждения оплаты.", "danger")
        return redirect(url_for("profile.index"))
    if not allowed_file(receipt.filename, ALLOWED_IMAGE_EXTENSIONS):
        flash("Поддерживаются изображения png, jpg, jpeg, gif или webp.", "danger")
        return redirect(url_for("profile.index"))

    filename = unique_filename(receipt.filename)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "topups")
    receipt.save(os.path.join(upload_dir, filename))
    receipt_path = f"uploads/topups/{filename}"

    db = get_db()
    db.execute(
        """
        INSERT INTO topup_requests (user_id, amount, receipt_path)
        VALUES (?, ?, ?)
        """,
        (g.user["id"], amount, receipt_path),
    )
    db.commit()
    flash("Заявка на пополнение отправлена админу.", "success")
    return redirect(url_for("profile.index"))


@bp.post("/nickname")
@login_required
def change_nickname():
    nickname = request.form.get("nickname", "").strip()
    error = validate_nickname(nickname)
    db = get_db()

    if error:
        flash(error, "danger")
    elif nickname_is_taken(db, nickname, current_user_id=g.user["id"]):
        flash("Такой никнейм уже занят.", "danger")
    else:
        db.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, g.user["id"]))
        db.commit()
        flash("Никнейм обновлён.", "success")
    return redirect(url_for("profile.index"))


@bp.post("/email/request")
@login_required
def request_email_change():
    new_email = request.form.get("new_email", "").strip().lower()
    if not new_email or "@" not in new_email:
        flash("Введите корректную новую почту.", "danger")
        return redirect(url_for("profile.index"))

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (new_email,)).fetchone()
    if existing is not None:
        flash("Такая почта уже занята.", "danger")
        return redirect(url_for("profile.index"))

    db.execute("UPDATE users SET pending_email = ? WHERE id = ?", (new_email, g.user["id"]))
    db.commit()
    flash("Новая почта сохранена как ожидающая подтверждения.", "success")
    return redirect(url_for("profile.index"))


@bp.post("/email/confirm")
@login_required
def confirm_email_change():
    current_password = request.form.get("current_password", "")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (g.user["id"],)).fetchone()

    if not user["pending_email"]:
        flash("Нет ожидающей смены почты.", "warning")
    elif not check_password_hash(user["password_hash"], current_password):
        flash("Текущий пароль введён неверно.", "danger")
    else:
        db.execute(
            "UPDATE users SET email = ?, pending_email = NULL WHERE id = ?",
            (user["pending_email"], g.user["id"]),
        )
        db.commit()
        flash("Почта изменена.", "success")
    return redirect(url_for("profile.index"))


@bp.post("/email/cancel")
@login_required
def cancel_email_change():
    db = get_db()
    db.execute("UPDATE users SET pending_email = NULL WHERE id = ?", (g.user["id"],))
    db.commit()
    flash("Смена почты отменена.", "info")
    return redirect(url_for("profile.index"))


@bp.post("/password")
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    new_password_confirm = request.form.get("new_password_confirm", "")

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (g.user["id"],)).fetchone()
    if not check_password_hash(user["password_hash"], current_password):
        flash("Старый пароль введён неверно.", "danger")
    elif len(new_password) < 6:
        flash("Новый пароль должен быть не короче 6 символов.", "danger")
    elif new_password != new_password_confirm:
        flash("Новые пароли не совпадают.", "danger")
    else:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), g.user["id"]),
        )
        db.commit()
        flash("Пароль изменён.", "success")
    return redirect(url_for("profile.index"))
