import os
import sqlite3
from datetime import date, timedelta

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = os.path.join(current_app.root_path, "schema.sql")
    with open(schema_path, encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
    ensure_runtime_schema()
    seed_db(db)
    db.commit()


def ensure_runtime_schema():
    db = get_db()
    tables = {
        row["name"]
        for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    if "users" not in tables:
        return

    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at TEXT,
            CHECK(sender_id != recipient_id),
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_chat_messages_pair
        ON chat_messages(sender_id, recipient_id, created_at);

        CREATE INDEX IF NOT EXISTS idx_chat_messages_recipient
        ON chat_messages(recipient_id, read_at, created_at);
        """
    )


def seed_db(db):
    users = [
        ("admin@example.com", "Admin_01", generate_password_hash("admin123"), "admin", 0),
        ("user@example.com", "User_01", generate_password_hash("user123"), "user", 2500),
    ]
    db.executemany(
        """
        INSERT INTO users (email, nickname, password_hash, role, balance)
        VALUES (?, ?, ?, ?, ?)
        """,
        users,
    )

    categories = ["Наборы", "Цифровое", "Услуги", "Оборудование", "Образование", "Мерч", "Общее"]
    db.executemany("INSERT INTO product_categories (name) VALUES (?)", [(name,) for name in categories])
    category_ids = {
        row["name"]: row["id"]
        for row in db.execute("SELECT id, name FROM product_categories").fetchall()
    }

    tags = [
        "старт",
        "подписка",
        "услуга",
        "популярное",
        "демо",
        "новинка",
        "локальное",
        "команда",
        "офлайн",
        "онлайн",
        "скидка",
        "премиум",
    ]
    db.executemany("INSERT INTO product_tags (name) VALUES (?)", [(name,) for name in tags])
    tag_ids = {
        row["name"]: row["id"]
        for row in db.execute("SELECT id, name FROM product_tags").fetchall()
    }

    products = [
        (
            1,
            category_ids["Наборы"],
            "Базовый набор",
            "Универсальный товар-заглушка для каталога хакатонного проекта.",
            1200,
            14,
            None,
            ["старт", "демо"],
        ),
        (
            1,
            category_ids["Цифровое"],
            "Премиум-доступ",
            "Пример цифрового товара с отдельной карточкой и покупкой через корзину.",
            2990,
            8,
            None,
            ["подписка", "популярное"],
        ),
        (
            2,
            category_ids["Услуги"],
            "Сервисная услуга",
            "Шаблон услуги, который можно переименовать под идею команды.",
            750,
            30,
            None,
            ["услуга", "демо"],
        ),
        (
            2,
            category_ids["Оборудование"],
            "Аренда ноутбука",
            "Пример физического товара или ресурса для бронирования командой.",
            1800,
            6,
            None,
            ["офлайн", "команда"],
        ),
        (
            1,
            category_ids["Образование"],
            "Мини-курс",
            "Учебный продукт: можно заменить на лекцию, интенсив или консультацию.",
            1490,
            20,
            None,
            ["онлайн", "старт"],
        ),
        (
            2,
            category_ids["Мерч"],
            "Фирменная футболка",
            "Пример товара с остатками, категорией и тегами.",
            990,
            25,
            None,
            ["локальное", "популярное"],
        ),
        (
            1,
            category_ids["Цифровое"],
            "API-пакет",
            "Цифровой набор лимитов или функций для проекта.",
            4200,
            12,
            None,
            ["премиум", "онлайн"],
        ),
        (
            2,
            category_ids["Наборы"],
            "Командный комплект",
            "Набор материалов для рабочей группы или демо-стенда.",
            2600,
            9,
            None,
            ["команда", "популярное"],
        ),
        (
            1,
            category_ids["Услуги"],
            "Настройка проекта",
            "Услуга по первичной настройке, которую удобно адаптировать под идею.",
            1350,
            18,
            None,
            ["услуга", "старт"],
        ),
        (
            2,
            category_ids["Оборудование"],
            "Демо-стенд",
            "Оборудование для презентации, выставки или внутреннего тестирования.",
            3500,
            4,
            None,
            ["офлайн", "премиум"],
        ),
        (
            1,
            category_ids["Образование"],
            "Разбор проекта",
            "Консультационный продукт с комментариями и оценками.",
            2100,
            15,
            None,
            ["услуга", "онлайн"],
        ),
        (
            2,
            category_ids["Мерч"],
            "Стикер-пак",
            "Недорогой товар для проверки корзины и оформления заказов.",
            250,
            100,
            None,
            ["скидка", "локальное"],
        ),
        (
            1,
            category_ids["Цифровое"],
            "Шаблон презентации",
            "Цифровой файл или набор материалов для питча.",
            690,
            40,
            None,
            ["демо", "онлайн"],
        ),
        (
            2,
            category_ids["Наборы"],
            "Стартовый пакет команды",
            "Комплект для онбординга участников проекта.",
            1750,
            11,
            None,
            ["команда", "новинка"],
        ),
        (
            1,
            category_ids["Общее"],
            "Универсальная позиция",
            "Нейтральный товар-заглушка для любой предметной области.",
            500,
            50,
            None,
            ["демо", "скидка"],
        ),
    ]
    for owner_id, category_id, name, description, price, stock, image_path, product_tags in products:
        cursor = db.execute(
            """
            INSERT INTO products (owner_id, category_id, name, description, price, stock, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (owner_id, category_id, name, description, price, stock, image_path),
        )
        product_id = cursor.lastrowid
        db.executemany(
            "INSERT INTO product_tag_links (product_id, tag_id) VALUES (?, ?)",
            [(product_id, tag_ids[tag_name]) for tag_name in product_tags],
        )

    reviews = [
        (1, 2, 5, "Хороший стартовый товар для проверки каталога."),
        (2, 2, 4, "Удобный пример цифрового товара."),
        (3, 1, 5, "Подходит как шаблон услуги."),
        (4, 1, 4, "Полезно для офлайн-команд."),
        (5, 2, 5, "Хорошо подходит для обучения."),
        (6, 1, 4, "Простой пример товара с остатками."),
        (7, 2, 5, "Отличный цифровой пакет."),
        (8, 1, 4, "Удобный командный набор."),
        (11, 2, 5, "Дешёвый товар для проверки корзины."),
        (14, 2, 4, "Хороший стартовый пакет."),
    ]
    db.executemany(
        """
        INSERT INTO product_reviews (product_id, user_id, rating, comment)
        VALUES (?, ?, ?, ?)
        """,
        reviews,
    )

    today = date.today()
    events = [
        (2, today.isoformat(), "Демо-встреча", "Пример события в календаре."),
        (2, (today + timedelta(days=3)).isoformat(), "Контрольная дата", "Можно заменить под проект."),
    ]
    db.executemany(
        """
        INSERT INTO calendar_events (user_id, event_date, title, description)
        VALUES (?, ?, ?, ?)
        """,
        events,
    )

    rows = [
        ("Задача A", 42, "new", "Строка для демонстрации таблицы.", 2),
        ("Задача B", 87, "in_progress", "Значения можно редактировать и удалять.", 2),
        ("Задача C", 15, "done", "Готовая строка для статистики.", 1),
    ]
    db.executemany(
        """
        INSERT INTO table_rows (name, amount, status, note, created_by)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )

    statistic_points = [
        ("Январь", 24),
        ("Февраль", 38),
        ("Март", 31),
        ("Апрель", 52),
        ("Май", 47),
    ]
    db.executemany(
        "INSERT INTO statistic_points (label, value) VALUES (?, ?)",
        statistic_points,
    )

    demo_messages = [
        (2, 1, "Здравствуйте! Хотел уточнить условия участия в хакатоне."),
        (1, 2, "Привет! Конечно, напиши, что именно интересно."),
    ]
    db.executemany(
        """
        INSERT INTO chat_messages (sender_id, recipient_id, body)
        VALUES (?, ?, ?)
        """,
        demo_messages,
    )


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("SQLite database initialized with demo data.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
