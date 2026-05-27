import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.utils import nickname_is_taken, validate_nickname


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        nickname = request.form.get("nickname", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        error = None

        if not email or "@" not in email:
            error = "Введите корректную почту."
        elif validate_nickname(nickname):
            error = validate_nickname(nickname)
        elif len(password) < 6:
            error = "Пароль должен быть не короче 6 символов."
        elif password != password_confirm:
            error = "Пароли не совпадают."

        db = get_db()
        if error is None and nickname_is_taken(db, nickname):
            error = "Такой никнейм уже занят."

        if error is None:
            try:
                db.execute(
                    """
                    INSERT INTO users (email, nickname, password_hash, role)
                    VALUES (?, ?, ?, 'user')
                    """,
                    (email, nickname, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = "Пользователь с такой почтой или никнеймом уже существует."
            else:
                flash("Аккаунт создан. Теперь можно войти.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Неверная почта или пароль.", "danger")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("Вы вошли в аккаунт.", "success")
            return redirect(url_for("main.index"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))
