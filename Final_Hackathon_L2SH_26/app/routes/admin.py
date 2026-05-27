from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.product_service import (
    ensure_category,
    ensure_tags,
    get_product_form_options,
    get_product_tag_ids,
    product_payload,
    replace_product_tags,
    save_product_image,
    validate_product,
)
from app.utils import roles_required


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@roles_required("admin")
def dashboard():
    db = get_db()
    counts = {
        "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "products": db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1").fetchone()[0],
        "orders": db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "pending_topups": db.execute(
            "SELECT COUNT(*) FROM topup_requests WHERE status = 'pending'"
        ).fetchone()[0],
    }
    topups = db.execute(
        """
        SELECT tr.*, u.email AS user_email
               , u.nickname AS user_nickname
        FROM topup_requests tr
        JOIN users u ON u.id = tr.user_id
        ORDER BY tr.created_at DESC
        LIMIT 12
        """
    ).fetchall()
    users = db.execute(
        """
        SELECT id, email, nickname, role, balance, created_at
        FROM users
        ORDER BY created_at DESC
        """
    ).fetchall()
    return render_template("admin/dashboard.html", counts=counts, topups=topups, users=users)


@bp.route("/products")
@roles_required("admin")
def products():
    db = get_db()
    product_rows = db.execute(
        """
        SELECT p.id,
               p.category_id,
               p.name,
               p.description,
               c.name AS category,
               p.price,
               p.stock,
               p.image_path,
               p.is_active,
               p.created_at,
               u.email AS owner_email,
               u.nickname AS owner_nickname,
               COALESCE((SELECT ROUND(AVG(rating), 1) FROM product_reviews WHERE product_id = p.id), 0) AS avg_rating
        FROM products p
        JOIN product_categories c ON c.id = p.category_id
        LEFT JOIN users u ON u.id = p.owner_id
        ORDER BY p.created_at DESC
        """
    ).fetchall()
    categories, tags = get_product_form_options(db)
    selected_tags_by_product = {}
    product_ids = [product["id"] for product in product_rows]
    if product_ids:
        placeholders = ", ".join("?" for _ in product_ids)
        rows = db.execute(
            f"""
            SELECT product_id, tag_id
            FROM product_tag_links
            WHERE product_id IN ({placeholders})
            """,
            product_ids,
        ).fetchall()
        for row in rows:
            selected_tags_by_product.setdefault(row["product_id"], set()).add(row["tag_id"])
    return render_template(
        "admin/products.html",
        products=product_rows,
        categories=categories,
        tags=tags,
        selected_tag_ids=set(),
        selected_tags_by_product=selected_tags_by_product,
    )


@bp.route("/products/new", methods=("GET", "POST"))
@roles_required("admin")
def product_new():
    db = get_db()
    categories, tags = get_product_form_options(db)
    selected_tag_ids = set()

    if request.method == "POST":
        payload = product_payload()
        selected_tag_ids = set(payload["tag_ids"])
        error = validate_product(payload)
        image_path = save_product_image(request.files.get("image"))
        if image_path is False:
            error = "Поддерживаются изображения png, jpg, jpeg, gif или webp."

        if error:
            flash(error, "danger")
        else:
            category_id = ensure_category(db, payload)
            tag_ids = ensure_tags(db, payload)
            db.execute(
                """
                INSERT INTO products (owner_id, category_id, name, description, price, stock, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    g.user["id"],
                    category_id,
                    payload["name"],
                    payload["description"],
                    payload["price"],
                    payload["stock"],
                    image_path,
                ),
            )
            product_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            replace_product_tags(db, product_id, tag_ids)
            db.commit()
            flash("Товар добавлен.", "success")
            return redirect(url_for("admin.products"))

    return render_template(
        "products/form.html",
        product=None,
        categories=categories,
        tags=tags,
        selected_tag_ids=selected_tag_ids,
        form_title="Добавить товар",
        back_url=url_for("admin.products"),
        show_active_toggle=False,
    )


@bp.route("/products/<int:product_id>/edit", methods=("GET", "POST"))
@roles_required("admin")
def product_edit(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)

    categories, tags = get_product_form_options(db)
    selected_tag_ids = get_product_tag_ids(db, product_id)

    if request.method == "POST":
        payload = product_payload()
        selected_tag_ids = set(payload["tag_ids"])
        error = validate_product(payload)
        image_path = save_product_image(request.files.get("image"))
        if image_path is False:
            error = "Поддерживаются изображения png, jpg, jpeg, gif или webp."
        if image_path is None:
            image_path = product["image_path"]

        if error:
            flash(error, "danger")
        else:
            category_id = ensure_category(db, payload)
            tag_ids = ensure_tags(db, payload)
            db.execute(
                """
                UPDATE products
                SET category_id = ?,
                    name = ?,
                    description = ?,
                    price = ?,
                    stock = ?,
                    image_path = ?,
                    is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    category_id,
                    payload["name"],
                    payload["description"],
                    payload["price"],
                    payload["stock"],
                    image_path,
                    1 if request.form.get("is_active") == "on" else 0,
                    product_id,
                ),
            )
            replace_product_tags(db, product_id, tag_ids)
            db.commit()
            flash("Товар обновлён.", "success")
            return redirect(url_for("admin.products"))

    return render_template(
        "products/form.html",
        product=product,
        categories=categories,
        tags=tags,
        selected_tag_ids=selected_tag_ids,
        form_title="Изменить товар",
        back_url=url_for("admin.products"),
        show_active_toggle=True,
    )


@bp.post("/products/<int:product_id>/delete")
@roles_required("admin")
def product_delete(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("Товар удалён. История заказов сохраняет название и цену покупки.", "info")
    return redirect(url_for("admin.products"))


@bp.post("/topups/<int:topup_id>/approve")
@roles_required("admin")
def approve_topup(topup_id):
    db = get_db()
    topup = db.execute("SELECT * FROM topup_requests WHERE id = ?", (topup_id,)).fetchone()
    if topup is None:
        abort(404)
    if topup["status"] != "pending":
        flash("Эта заявка уже обработана.", "warning")
        return redirect(url_for("admin.dashboard"))

    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (topup["amount"], topup["user_id"]))
    db.execute(
        """
        UPDATE topup_requests
        SET status = 'approved',
            reviewed_by = ?,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (g.user["id"], topup_id),
    )
    db.commit()
    flash("Пополнение подтверждено, баланс обновлён.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.post("/topups/<int:topup_id>/decline")
@roles_required("admin")
def decline_topup(topup_id):
    comment = request.form.get("admin_comment", "").strip()
    db = get_db()
    topup = db.execute("SELECT * FROM topup_requests WHERE id = ?", (topup_id,)).fetchone()
    if topup is None:
        abort(404)
    if topup["status"] != "pending":
        flash("Эта заявка уже обработана.", "warning")
    else:
        db.execute(
            """
            UPDATE topup_requests
            SET status = 'declined',
                admin_comment = ?,
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (comment, g.user["id"], topup_id),
        )
        db.commit()
        flash("Заявка отклонена.", "info")
    return redirect(url_for("admin.dashboard"))


@bp.post("/users/<int:user_id>/role")
@roles_required("admin")
def update_user_role(user_id):
    role = request.form.get("role", "user")
    if role not in {"user", "manager", "admin"}:
        flash("Неизвестная роль.", "danger")
        return redirect(url_for("admin.dashboard"))

    db = get_db()
    if user_id == g.user["id"] and role != "admin":
        flash("Нельзя снять роль админа с текущего аккаунта.", "warning")
    else:
        db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        db.commit()
        flash("Роль пользователя обновлена.", "success")
    return redirect(url_for("admin.dashboard"))
