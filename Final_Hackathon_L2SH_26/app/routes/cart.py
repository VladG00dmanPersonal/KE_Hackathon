from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import login_required


bp = Blueprint("cart", __name__, url_prefix="/cart")


def get_cart_items():
    return get_db().execute(
        """
        SELECT
            ci.id,
            ci.product_id,
            ci.quantity,
            p.name,
            p.price,
            p.stock,
            p.image_path,
            p.is_active,
            ci.quantity * p.price AS subtotal
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
        WHERE ci.user_id = ?
        ORDER BY ci.created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()


@bp.route("/")
@login_required
def index():
    items = get_cart_items()
    total = sum(item["subtotal"] for item in items if item["is_active"])
    return render_template("cart.html", items=items, total=total)


@bp.post("/add/<int:product_id>")
@login_required
def add(product_id):
    quantity = request.form.get("quantity", 1, type=int)
    quantity = max(quantity, 1)
    db = get_db()
    product = db.execute(
        "SELECT id, name, stock, is_active FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if product is None or not product["is_active"]:
        flash("Товар не найден.", "danger")
    elif product["stock"] <= 0:
        flash("Товара нет в наличии.", "warning")
    else:
        db.execute(
            """
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (g.user["id"], product_id, quantity),
        )
        db.commit()
        flash("Товар добавлен в корзину.", "success")
    return redirect(request.referrer or url_for("products.index"))


@bp.post("/update/<int:item_id>")
@login_required
def update(item_id):
    quantity = request.form.get("quantity", 1, type=int)
    db = get_db()
    item = db.execute(
        "SELECT id FROM cart_items WHERE id = ? AND user_id = ?",
        (item_id, g.user["id"]),
    ).fetchone()
    if item is None:
        flash("Позиция корзины не найдена.", "danger")
    elif quantity <= 0:
        db.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (item_id, g.user["id"]))
        db.commit()
        flash("Позиция удалена из корзины.", "info")
    else:
        db.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?",
            (quantity, item_id, g.user["id"]),
        )
        db.commit()
        flash("Корзина обновлена.", "success")
    return redirect(url_for("cart.index"))


@bp.post("/remove/<int:item_id>")
@login_required
def remove(item_id):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (item_id, g.user["id"]))
    db.commit()
    flash("Товар удалён из корзины.", "info")
    return redirect(url_for("cart.index"))


@bp.post("/checkout")
@login_required
def checkout():
    db = get_db()
    items = get_cart_items()
    if not items:
        flash("Корзина пуста.", "warning")
        return redirect(url_for("cart.index"))

    for item in items:
        if not item["is_active"]:
            flash(f"Товар «{item['name']}» больше недоступен.", "danger")
            return redirect(url_for("cart.index"))
        if item["quantity"] > item["stock"]:
            flash(f"Недостаточно товара «{item['name']}» на складе.", "danger")
            return redirect(url_for("cart.index"))

    total = sum(item["subtotal"] for item in items)
    user = db.execute("SELECT balance FROM users WHERE id = ?", (g.user["id"],)).fetchone()
    if user["balance"] < total:
        flash("Недостаточно средств. Отправьте заявку на пополнение в профиле.", "danger")
        return redirect(url_for("cart.index"))

    order_cursor = db.execute(
        "INSERT INTO orders (user_id, total, status) VALUES (?, ?, 'paid')",
        (g.user["id"], total),
    )
    order_id = order_cursor.lastrowid
    for item in items:
        db.execute(
            """
            INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                item["product_id"],
                item["name"],
                item["price"],
                item["quantity"],
                item["subtotal"],
            ),
        )
        db.execute(
            "UPDATE products SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )

    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total, g.user["id"]))
    db.execute("DELETE FROM cart_items WHERE user_id = ?", (g.user["id"],))
    db.commit()
    flash("Заказ оформлен и оплачен с баланса.", "success")
    return redirect(url_for("profile.index"))

