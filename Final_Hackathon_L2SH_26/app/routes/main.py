from flask import Blueprint, render_template

from app.db import get_db


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    db = get_db()
    counters = {
        "products": db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1").fetchone()[0],
        "orders": db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "events": db.execute("SELECT COUNT(*) FROM calendar_events").fetchone()[0],
        "rows": db.execute("SELECT COUNT(*) FROM table_rows").fetchone()[0],
    }
    latest_products = db.execute(
        """
        SELECT p.id,
               p.category_id,
               p.name,
               p.description,
               c.name AS category,
               p.price,
               p.stock,
               p.image_path,
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
        WHERE p.is_active = 1
        ORDER BY p.created_at DESC
        LIMIT 4
        """
    ).fetchall()
    return render_template("index.html", counters=counters, latest_products=latest_products)
