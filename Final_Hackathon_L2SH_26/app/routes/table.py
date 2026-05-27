from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import login_required


bp = Blueprint("table", __name__, url_prefix="/table")


@bp.route("/")
@login_required
def index():
    rows = get_db().execute(
        """
        SELECT tr.*, u.email AS creator_email
        FROM table_rows tr
        LEFT JOIN users u ON u.id = tr.created_by
        ORDER BY tr.created_at DESC
        """
    ).fetchall()
    return render_template("table/index.html", rows=rows)


def parse_row_form():
    return {
        "name": request.form.get("name", "").strip(),
        "amount": request.form.get("amount", 0, type=float),
        "status": request.form.get("status", "new"),
        "note": request.form.get("note", "").strip(),
    }


def validate_row(payload):
    if not payload["name"]:
        return "Введите название строки."
    if payload["amount"] is None:
        return "Введите числовое значение."
    if payload["status"] not in {"new", "in_progress", "done"}:
        return "Неизвестный статус."
    return None


@bp.post("/add")
@login_required
def add():
    payload = parse_row_form()
    error = validate_row(payload)
    if error:
        flash(error, "danger")
    else:
        db = get_db()
        db.execute(
            """
            INSERT INTO table_rows (name, amount, status, note, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload["name"], payload["amount"], payload["status"], payload["note"], g.user["id"]),
        )
        db.commit()
        flash("Строка добавлена.", "success")
    return redirect(url_for("table.index"))


@bp.route("/<int:row_id>/edit", methods=("GET", "POST"))
@login_required
def edit(row_id):
    db = get_db()
    row = db.execute("SELECT * FROM table_rows WHERE id = ?", (row_id,)).fetchone()
    if row is None:
        abort(404)

    if request.method == "POST":
        payload = parse_row_form()
        error = validate_row(payload)
        if error:
            flash(error, "danger")
        else:
            db.execute(
                """
                UPDATE table_rows
                SET name = ?,
                    amount = ?,
                    status = ?,
                    note = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (payload["name"], payload["amount"], payload["status"], payload["note"], row_id),
            )
            db.commit()
            flash("Строка обновлена.", "success")
            return redirect(url_for("table.index"))

    return render_template("table/edit.html", row=row)


@bp.post("/<int:row_id>/delete")
@login_required
def delete(row_id):
    db = get_db()
    db.execute("DELETE FROM table_rows WHERE id = ?", (row_id,))
    db.commit()
    flash("Строка удалена.", "info")
    return redirect(url_for("table.index"))

