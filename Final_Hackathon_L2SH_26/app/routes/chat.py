from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import login_required


bp = Blueprint("chat", __name__, url_prefix="/chat")

MAX_MESSAGE_LENGTH = 2000


def _fetch_chat_users(db, current_user_id):
    return db.execute(
        """
        SELECT
            u.id,
            u.email,
            u.nickname,
            (
                SELECT cm.body
                FROM chat_messages cm
                WHERE
                    (cm.sender_id = ? AND cm.recipient_id = u.id)
                    OR
                    (cm.sender_id = u.id AND cm.recipient_id = ?)
                ORDER BY cm.created_at DESC, cm.id DESC
                LIMIT 1
            ) AS last_message,
            (
                SELECT cm.created_at
                FROM chat_messages cm
                WHERE
                    (cm.sender_id = ? AND cm.recipient_id = u.id)
                    OR
                    (cm.sender_id = u.id AND cm.recipient_id = ?)
                ORDER BY cm.created_at DESC, cm.id DESC
                LIMIT 1
            ) AS last_message_at,
            (
                SELECT COUNT(*)
                FROM chat_messages cm
                WHERE cm.sender_id = u.id
                  AND cm.recipient_id = ?
                  AND cm.read_at IS NULL
            ) AS unread_count
        FROM users u
        WHERE u.id != ?
        ORDER BY
            CASE WHEN last_message_at IS NULL THEN 1 ELSE 0 END,
            last_message_at DESC,
            u.nickname COLLATE NOCASE,
            u.email COLLATE NOCASE
        """,
        (
            current_user_id,
            current_user_id,
            current_user_id,
            current_user_id,
            current_user_id,
            current_user_id,
        ),
    ).fetchall()


def _fetch_conversation(db, current_user_id, other_user_id):
    return db.execute(
        """
        SELECT
            cm.id,
            cm.sender_id,
            cm.recipient_id,
            cm.body,
            cm.created_at,
            cm.read_at,
            u.nickname AS sender_nickname,
            u.email AS sender_email
        FROM chat_messages cm
        JOIN users u ON u.id = cm.sender_id
        WHERE
            (cm.sender_id = ? AND cm.recipient_id = ?)
            OR
            (cm.sender_id = ? AND cm.recipient_id = ?)
        ORDER BY cm.created_at, cm.id
        """,
        (current_user_id, other_user_id, other_user_id, current_user_id),
    ).fetchall()


@bp.route("/")
@login_required
def index():
    db = get_db()
    chat_users = _fetch_chat_users(db, g.user["id"])
    selected_user_id = request.args.get("user_id", type=int)

    if not chat_users:
        return render_template("chat.html", chat_users=[], selected_user=None, conversation=[])

    if selected_user_id is None:
        selected_user_id = chat_users[0]["id"]

    if selected_user_id == g.user["id"] or selected_user_id not in {user["id"] for user in chat_users}:
        flash("Выберите корректного собеседника для чата.", "warning")
        return redirect(url_for("chat.index"))

    db.execute(
        """
        UPDATE chat_messages
        SET read_at = CURRENT_TIMESTAMP
        WHERE sender_id = ? AND recipient_id = ? AND read_at IS NULL
        """,
        (selected_user_id, g.user["id"]),
    )
    db.commit()

    chat_users = _fetch_chat_users(db, g.user["id"])
    selected_user = next((user for user in chat_users if user["id"] == selected_user_id), None)
    if selected_user is None:
        flash("Собеседник больше недоступен.", "warning")
        return redirect(url_for("chat.index"))
    conversation = _fetch_conversation(db, g.user["id"], selected_user_id)

    return render_template(
        "chat.html",
        chat_users=chat_users,
        selected_user=selected_user,
        conversation=conversation,
        max_message_length=MAX_MESSAGE_LENGTH,
    )


@bp.post("/send")
@login_required
def send():
    recipient_id = request.form.get("recipient_id", type=int)
    body = request.form.get("body", "").strip()
    redirect_url = url_for("chat.index", user_id=recipient_id) if recipient_id else url_for("chat.index")

    if recipient_id is None:
        flash("Не выбран получатель сообщения.", "danger")
        return redirect(url_for("chat.index"))
    if recipient_id == g.user["id"]:
        flash("Нельзя отправить сообщение самому себе.", "danger")
        return redirect(url_for("chat.index"))
    if not body:
        flash("Введите текст сообщения.", "danger")
        return redirect(redirect_url)
    if len(body) > MAX_MESSAGE_LENGTH:
        flash(f"Сообщение должно быть не длиннее {MAX_MESSAGE_LENGTH} символов.", "danger")
        return redirect(redirect_url)

    db = get_db()
    recipient = db.execute(
        "SELECT id FROM users WHERE id = ? AND id != ?",
        (recipient_id, g.user["id"]),
    ).fetchone()
    if recipient is None:
        flash("Получатель не найден.", "danger")
        return redirect(url_for("chat.index"))

    db.execute(
        """
        INSERT INTO chat_messages (sender_id, recipient_id, body)
        VALUES (?, ?, ?)
        """,
        (g.user["id"], recipient_id, body),
    )
    db.commit()
    return redirect(redirect_url)
