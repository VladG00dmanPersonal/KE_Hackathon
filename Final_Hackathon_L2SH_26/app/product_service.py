import os

from flask import current_app, request

from app.utils import ALLOWED_IMAGE_EXTENSIONS, allowed_file, unique_filename


def save_product_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename, ALLOWED_IMAGE_EXTENSIONS):
        return False

    filename = unique_filename(file_storage.filename)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "products")
    file_storage.save(os.path.join(upload_dir, filename))
    return f"uploads/products/{filename}"


def product_payload():
    return {
        "name": request.form.get("name", "").strip(),
        "description": request.form.get("description", "").strip(),
        "category_id": request.form.get("category_id", type=int),
        "new_category": request.form.get("new_category", "").strip(),
        "price": request.form.get("price", 0, type=float),
        "stock": request.form.get("stock", 0, type=int),
        "tag_ids": request.form.getlist("tag_ids", type=int),
        "new_tags": request.form.get("new_tags", "").strip(),
    }


def validate_product(payload):
    if not payload["name"]:
        return "Введите название товара."
    if not payload["category_id"] and not payload["new_category"]:
        return "Выберите категорию или создайте новую."
    if payload["price"] is None or payload["price"] < 0:
        return "Цена не может быть отрицательной."
    if payload["stock"] is None or payload["stock"] < 0:
        return "Остаток не может быть отрицательным."
    return None


def get_product_form_options(db):
    categories = db.execute(
        "SELECT id, name FROM product_categories ORDER BY name"
    ).fetchall()
    tags = db.execute("SELECT id, name FROM product_tags ORDER BY name").fetchall()
    return categories, tags


def get_product_tag_ids(db, product_id):
    rows = db.execute(
        "SELECT tag_id FROM product_tag_links WHERE product_id = ?",
        (product_id,),
    ).fetchall()
    return {row["tag_id"] for row in rows}


def ensure_category(db, payload):
    if payload["new_category"]:
        db.execute(
            "INSERT OR IGNORE INTO product_categories (name) VALUES (?)",
            (payload["new_category"],),
        )
        row = db.execute(
            "SELECT id FROM product_categories WHERE name = ?",
            (payload["new_category"],),
        ).fetchone()
        return row["id"]
    return payload["category_id"]


def normalize_new_tags(raw_tags):
    normalized = []
    seen = set()
    for tag in raw_tags.replace(";", ",").split(","):
        name = tag.strip()
        key = name.lower()
        if name and key not in seen:
            normalized.append(name)
            seen.add(key)
    return normalized


def ensure_tags(db, payload):
    tag_ids = set(payload["tag_ids"])
    for tag_name in normalize_new_tags(payload["new_tags"]):
        db.execute("INSERT OR IGNORE INTO product_tags (name) VALUES (?)", (tag_name,))
        row = db.execute("SELECT id FROM product_tags WHERE name = ?", (tag_name,)).fetchone()
        tag_ids.add(row["id"])
    return sorted(tag_ids)


def replace_product_tags(db, product_id, tag_ids):
    db.execute("DELETE FROM product_tag_links WHERE product_id = ?", (product_id,))
    db.executemany(
        "INSERT INTO product_tag_links (product_id, tag_id) VALUES (?, ?)",
        [(product_id, tag_id) for tag_id in tag_ids],
    )

