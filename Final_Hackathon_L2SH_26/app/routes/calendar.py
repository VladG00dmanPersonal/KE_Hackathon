from calendar import Calendar
from datetime import date, datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import login_required


bp = Blueprint("calendar", __name__, url_prefix="/calendar")

MONTH_NAMES = [
    "",
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]


def clamp_month(year, month):
    if month < 1:
        return year - 1, 12
    if month > 12:
        return year + 1, 1
    return year, month


def parse_iso_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@bp.route("/")
@login_required
def index():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)
    year, month = clamp_month(year, month)

    start = date(year, month, 1)
    end_year, end_month = clamp_month(year, month + 1)
    end = date(end_year, end_month, 1)

    rows = get_db().execute(
        """
        SELECT id, event_date, title, description
        FROM calendar_events
        WHERE user_id = ? AND event_date >= ? AND event_date < ?
        ORDER BY event_date, created_at
        """,
        (g.user["id"], start.isoformat(), end.isoformat()),
    ).fetchall()
    events_by_date = {}
    for row in rows:
        events_by_date.setdefault(row["event_date"], []).append(row)

    weeks = Calendar(firstweekday=0).monthdatescalendar(year, month)
    prev_year, prev_month = clamp_month(year, month - 1)
    next_year, next_month = clamp_month(year, month + 1)
    return render_template(
        "calendar/index.html",
        weeks=weeks,
        events_by_date=events_by_date,
        year=year,
        month=month,
        month_name=MONTH_NAMES[month],
        month_options=list(enumerate(MONTH_NAMES))[1:],
        today=today,
        prev_year=prev_year,
        prev_month=prev_month,
        prev_month_name=MONTH_NAMES[prev_month],
        next_year=next_year,
        next_month=next_month,
        next_month_name=MONTH_NAMES[next_month],
    )


@bp.route("/day/<event_date>")
@login_required
def day(event_date):
    try:
        selected_day = parse_iso_date(event_date)
    except ValueError:
        flash("Некорректная дата.", "danger")
        return redirect(url_for("calendar.index"))

    events = get_db().execute(
        """
        SELECT id, event_date, title, description, created_at
        FROM calendar_events
        WHERE user_id = ? AND event_date = ?
        ORDER BY created_at
        """,
        (g.user["id"], selected_day.isoformat()),
    ).fetchall()
    return render_template(
        "calendar/day.html",
        selected_day=selected_day,
        events=events,
        month_name=MONTH_NAMES[selected_day.month],
    )


@bp.post("/add")
@login_required
def add():
    event_date = request.form.get("event_date", "")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not event_date or not title:
        flash("Укажите дату и название события.", "danger")
    else:
        db = get_db()
        db.execute(
            """
            INSERT INTO calendar_events (user_id, event_date, title, description)
            VALUES (?, ?, ?, ?)
            """,
            (g.user["id"], event_date, title, description),
        )
        db.commit()
        flash("Событие добавлено.", "success")
    return redirect(request.form.get("next") or request.referrer or url_for("calendar.index"))


@bp.post("/delete/<int:event_id>")
@login_required
def delete(event_id):
    db = get_db()
    db.execute(
        "DELETE FROM calendar_events WHERE id = ? AND user_id = ?",
        (event_id, g.user["id"]),
    )
    db.commit()
    flash("Событие удалено.", "info")
    return redirect(request.referrer or url_for("calendar.index"))
