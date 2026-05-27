import csv
from io import BytesIO
from io import StringIO

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure

from flask import Blueprint, Response, abort, jsonify, render_template, request

from app.db import get_db
from app.utils import login_required


bp = Blueprint("stats", __name__, url_prefix="/stats")


@bp.route("/")
@login_required
def index():
    return render_template("stats.html")


def stats_payload():
    db = get_db()
    status_rows = db.execute(
        """
        SELECT status AS label, COUNT(*) AS value
        FROM table_rows
        GROUP BY status
        ORDER BY status
        """
    ).fetchall()
    order_rows = db.execute(
        """
        SELECT DATE(created_at) AS label, SUM(total) AS value
        FROM orders
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        LIMIT 14
        """
    ).fetchall()
    points = db.execute(
        """
        SELECT label, value
        FROM statistic_points
        ORDER BY id
        """
    ).fetchall()
    return {
        "statuses": [dict(row) for row in status_rows],
        "orders": [dict(row) for row in order_rows],
        "points": [dict(row) for row in points],
    }


@bp.route("/data")
@login_required
def data():
    return jsonify(stats_payload())


def chart_theme():
    if request.args.get("theme") == "dark":
        return {
            "figure": "#151a22",
            "axes": "#1d2430",
            "text": "#e7ebf0",
            "muted": "#aab3c1",
            "grid": "#333c4d",
            "accent": "#7aa2ff",
            "green": "#56d08f",
            "yellow": "#f4c56a",
            "red": "#ff7a70",
            "bar": "#7aa2ff",
        }
    return {
        "figure": "#f7f9fb",
        "axes": "#ffffff",
        "text": "#20242a",
        "muted": "#667085",
        "grid": "#d9dee7",
        "accent": "#1d4ed8",
        "green": "#087443",
        "yellow": "#9a6700",
        "red": "#b42318",
        "bar": "#1d4ed8",
    }


def chart_response(fig):
    output = BytesIO()
    fig.savefig(output, format="png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    output.seek(0)
    return Response(output.getvalue(), mimetype="image/png")


def prepare_axes(title, ylabel):
    colors = chart_theme()
    fig = Figure(figsize=(7.2, 3.8), dpi=180, facecolor=colors["figure"], layout="constrained")
    ax = fig.add_subplot(111)
    ax.set_facecolor(colors["axes"])
    ax.set_title(title, color=colors["text"], fontsize=14, fontweight="bold", pad=14)
    ax.set_ylabel(ylabel, color=colors["muted"], fontsize=10)
    ax.tick_params(axis="x", colors=colors["muted"], labelrotation=0)
    ax.tick_params(axis="y", colors=colors["muted"])
    ax.grid(True, axis="y", color=colors["grid"], linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(colors["grid"])
    ax.spines["bottom"].set_color(colors["grid"])
    return fig, ax, colors


def empty_chart(title):
    fig, ax, colors = prepare_axes(title, "Значение")
    ax.text(0.5, 0.5, "Нет данных", ha="center", va="center", transform=ax.transAxes, color=colors["muted"], fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


@bp.route("/chart/<kind>.png")
@login_required
def chart(kind):
    payload = stats_payload()
    if kind not in {"statuses", "orders", "points"}:
        abort(404)

    rows = payload[kind]
    if not rows:
        titles = {
            "statuses": "Статусы строк",
            "orders": "Оплаченные заказы",
            "points": "Пример метрик",
        }
        return chart_response(empty_chart(titles[kind]))

    labels = [str(row["label"]) for row in rows]
    values = [float(row["value"] or 0) for row in rows]

    if kind == "statuses":
        fig, ax, colors = prepare_axes("Статусы строк", "Количество")
        palette = [colors["accent"], colors["yellow"], colors["green"], colors["red"]]
        bars = ax.bar(labels, values, color=[palette[index % len(palette)] for index in range(len(values))], width=0.55)
        ax.bar_label(bars, labels=[f"{value:g}" for value in values], padding=4, color=colors["text"], fontsize=9)
        ax.margins(y=0.18)
    elif kind == "orders":
        fig, ax, colors = prepare_axes("Оплаченные заказы", "Сумма")
        bars = ax.bar(labels, values, color=colors["green"], width=0.52)
        ax.bar_label(bars, labels=[f"{value:g}" for value in values], padding=4, color=colors["text"], fontsize=9)
        ax.margins(y=0.18)
    else:
        fig, ax, colors = prepare_axes("Пример метрик", "Значение")
        x_positions = list(range(len(labels)))
        ax.plot(x_positions, values, color=colors["accent"], linewidth=2.8, marker="o", markersize=6)
        ax.fill_between(x_positions, values, color=colors["accent"], alpha=0.14)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels)
        for x_value, y_value in zip(x_positions, values):
            ax.annotate(f"{y_value:g}", (x_value, y_value), textcoords="offset points", xytext=(0, 9), ha="center", color=colors["text"], fontsize=9)
        ax.margins(x=0.04, y=0.18)

    return chart_response(fig)


@bp.route("/export.csv")
@login_required
def export_csv():
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name, amount, status, note, created_at, updated_at
        FROM table_rows
        ORDER BY created_at DESC
        """
    ).fetchall()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "amount", "status", "note", "created_at", "updated_at"])
    for row in rows:
        writer.writerow([row["id"], row["name"], row["amount"], row["status"], row["note"], row["created_at"], row["updated_at"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=stats_export.csv"},
    )
