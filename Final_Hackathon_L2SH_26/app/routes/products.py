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
from app.utils import login_required


bp = Blueprint("products", __name__, url_prefix="/products")


PRODUCT_LIST_SELECT = """
    SELECT
        p.id,
        p.owner_id,
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
        COALESCE((SELECT ROUND(AVG(rating), 1) FROM product_reviews WHERE product_id = p.id), 0) AS avg_rating,
        (SELECT COUNT(*) FROM product_reviews WHERE product_id = p.id) AS review_count,
        (SELECT GROUP_CONCAT(tag_name, ', ')
         FROM (
             SELECT t.name AS tag_name
             FROM product_tag_links ptl
             JOIN product_tags t ON t.id = ptl.tag_id
             WHERE ptl.product_id = p.id
             ORDER BY t.name
         )) AS tags,
        (SELECT GROUP_CONCAT(tag_pair, '||')
         FROM (
             SELECT t.id || '~' || t.name AS tag_pair
             FROM product_tag_links ptl
             JOIN product_tags t ON t.id = ptl.tag_id
             WHERE ptl.product_id = p.id
             ORDER BY t.name
         )) AS tag_pairs
    FROM products p
    JOIN product_categories c ON c.id = p.category_id
    LEFT JOIN users u ON u.id = p.owner_id
"""


def can_edit_product(product):
    return g.user is not None and (g.user["role"] == "admin" or product["owner_id"] == g.user["id"])


@bp.route("/")
def index():
    query = request.args.get("q", "").strip()
    legacy_category_id = request.args.get("category_id", type=int)
    category_ids = request.args.getlist("category_ids", type=int)
    if legacy_category_id:
        category_ids.append(legacy_category_id)
    category_ids = list(dict.fromkeys([category_id for category_id in category_ids if category_id]))
    tag_id = request.args.get("tag_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "new")
    view_mode = request.args.get("view", "grid")
    if view_mode not in {"grid", "list"}:
        view_mode = "grid"

    filters = ["p.is_active = 1"]
    params = []

    if query:
        filters.append("LOWER(p.name) LIKE ?")
        params.append(f"%{query.lower()}%")
    if category_ids:
        placeholders = ", ".join("?" for _ in category_ids)
        filters.append(f"p.category_id IN ({placeholders})")
        params.extend(category_ids)
    if tag_id:
        filters.append(
            """
            EXISTS (
                SELECT 1
                FROM product_tag_links filter_ptl
                WHERE filter_ptl.product_id = p.id AND filter_ptl.tag_id = ?
            )
            """
        )
        params.append(tag_id)
    if min_price is not None:
        filters.append("p.price >= ?")
        params.append(min_price)
    if max_price is not None:
        filters.append("p.price <= ?")
        params.append(max_price)

    order_by = {
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "name": "p.name ASC",
        "rating": "avg_rating DESC, review_count DESC, p.created_at DESC",
        "new": "p.created_at DESC",
    }.get(sort, "p.created_at DESC")

    db = get_db()
    products = db.execute(
        f"""
        {PRODUCT_LIST_SELECT}
        WHERE {' AND '.join(filters)}
        ORDER BY {order_by}
        """,
        params,
    ).fetchall()
    categories = db.execute(
        "SELECT id, name FROM product_categories ORDER BY name"
    ).fetchall()
    tags = db.execute("SELECT id, name FROM product_tags ORDER BY name").fetchall()
    return render_template(
        "products/index.html",
        products=products,
        categories=categories,
        tags=tags,
        filters={
            "q": query,
            "category_ids": category_ids,
            "tag_id": tag_id,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
            "view_mode": view_mode,
        },
        product=None,
        selected_tag_ids=set(),
        show_active_toggle=False,
    )


@bp.route("/mine")
@login_required
def mine():
    db = get_db()
    products = db.execute(
        f"""
        {PRODUCT_LIST_SELECT}
        WHERE p.owner_id = ?
        ORDER BY p.created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()
    categories, tags = get_product_form_options(db)
    selected_tags_by_product = {}
    product_ids = [product["id"] for product in products]
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
        "products/mine.html",
        products=products,
        categories=categories,
        tags=tags,
        product=None,
        selected_tag_ids=set(),
        selected_tags_by_product=selected_tags_by_product,
        show_active_toggle=False,
    )


@bp.route("/new", methods=("GET", "POST"))
@login_required
def new():
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
            cursor = db.execute(
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
            product_id = cursor.lastrowid
            replace_product_tags(db, product_id, tag_ids)
            db.commit()
            flash("Товар добавлен в каталог.", "success")
            return redirect(url_for("products.detail", product_id=product_id))

    return render_template(
        "products/form.html",
        product=None,
        categories=categories,
        tags=tags,
        selected_tag_ids=selected_tag_ids,
        form_title="Добавить товар",
        back_url=url_for("products.index"),
        show_active_toggle=False,
    )


@bp.route("/<int:product_id>")
def detail(product_id):
    db = get_db()
    product = db.execute(
        f"""
        {PRODUCT_LIST_SELECT}
        WHERE p.id = ? AND p.is_active = 1
        """,
        (product_id,),
    ).fetchone()
    if product is None:
        abort(404)

    tag_rows = db.execute(
        """
        SELECT t.id, t.name
        FROM product_tag_links ptl
        JOIN product_tags t ON t.id = ptl.tag_id
        WHERE ptl.product_id = ?
        ORDER BY t.name
        """,
        (product_id,),
    ).fetchall()
    reviews = db.execute(
        """
        SELECT pr.*, u.email AS user_email, u.nickname AS user_nickname
        FROM product_reviews pr
        JOIN users u ON u.id = pr.user_id
        WHERE pr.product_id = ?
        ORDER BY pr.updated_at DESC
        """,
        (product_id,),
    ).fetchall()
    user_review = None
    if g.user:
        user_review = db.execute(
            """
            SELECT rating, comment
            FROM product_reviews
            WHERE product_id = ? AND user_id = ?
            """,
            (product_id, g.user["id"]),
        ).fetchone()
    categories, all_tags = get_product_form_options(db)

    return render_template(
        "products/detail.html",
        product=product,
        tags=tag_rows,
        categories=categories,
        all_tags=all_tags,
        selected_tag_ids=get_product_tag_ids(db, product_id),
        show_active_toggle=False,
        reviews=reviews,
        user_review=user_review,
        can_edit=can_edit_product(product),
    )


@bp.route("/<int:product_id>/edit", methods=("GET", "POST"))
@login_required
def edit(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)
    if not can_edit_product(product):
        abort(403)

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
                    product_id,
                ),
            )
            replace_product_tags(db, product_id, tag_ids)
            db.commit()
            flash("Товар обновлён.", "success")
            return redirect(url_for("products.detail", product_id=product_id))

    return render_template(
        "products/form.html",
        product=product,
        categories=categories,
        tags=tags,
        selected_tag_ids=selected_tag_ids,
        form_title="Изменить товар",
        back_url=url_for("products.mine"),
        show_active_toggle=False,
    )


@bp.post("/<int:product_id>/delete")
@login_required
def delete(product_id):
    db = get_db()
    product = db.execute("SELECT id, owner_id FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)
    if not can_edit_product(product):
        abort(403)

    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("Товар удалён.", "info")
    return redirect(url_for("products.mine"))


@bp.post("/<int:product_id>/review")
@login_required
def review(product_id):
    db = get_db()
    product = db.execute(
        "SELECT id FROM products WHERE id = ? AND is_active = 1",
        (product_id,),
    ).fetchone()
    if product is None:
        abort(404)

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()
    if rating is None or rating < 1 or rating > 5:
        flash("Оценка должна быть от 1 до 5.", "danger")
    else:
        db.execute(
            """
            INSERT INTO product_reviews (product_id, user_id, rating, comment)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(product_id, user_id)
            DO UPDATE SET
                rating = excluded.rating,
                comment = excluded.comment,
                updated_at = CURRENT_TIMESTAMP
            """,
            (product_id, g.user["id"], rating, comment),
        )
        db.commit()
        flash("Оценка и комментарий сохранены.", "success")
    return redirect(url_for("products.detail", product_id=product_id))
