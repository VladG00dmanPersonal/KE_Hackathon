# Подробное руководство по расширению проекта

Это руководство написано под текущий проект. Цель простая: чтобы даже джун мог открыть код, понять, где что лежит, и без магии добавить новую рабочую страницу с логикой, данными и интерфейсом.

## 1. Что это за проект

Текущий стек:

- Python
- Flask
- SQLite
- Jinja2-шаблоны
- Обычный CSS
- Обычный JavaScript без сборщика
- Bootstrap через CDN

Важно понять главное:

- это не React и не SPA;
- страница собирается на сервере через `render_template(...)`;
- данные хранятся в SQLite;
- почти вся серверная логика живет в `app/routes/*.py`;
- общие помощники вынесены в `app/utils.py`, `app/db.py`, `app/product_service.py`.

Если упростить, приложение работает так:

1. Пользователь открывает URL.
2. Flask находит нужный route.
3. Route читает данные из базы и/или обрабатывает форму.
4. Route отдает HTML-шаблон через `render_template(...)`.
5. Браузер показывает страницу.
6. Если на странице есть форма, пользователь отправляет `POST`.
7. Route валидирует данные, пишет их в БД, показывает `flash` и делает `redirect`.

Это называется server-side rendering + классический `POST -> redirect -> GET`.

## 2. Быстрая карта проекта

```text
run.py
requirements.txt
README.md
docs/
  developer-guide-ru.md
app/
  __init__.py
  db.py
  schema.sql
  utils.py
  product_service.py
  routes/
    main.py
    auth.py
    products.py
    cart.py
    profile.py
    admin.py
    calendar.py
    table.py
    stats.py
    forms.py
    chat.py
    advertisements.py
  templates/
    base.html
    404.html
    components/
    auth/
    admin/
    products/
    calendar/
    table/
    forms/
  static/
    css/styles.css
    js/
    uploads/
instance/
  hackathon.sqlite
```

Что за что отвечает:

- `run.py` — точка запуска Flask.
- `app/__init__.py` — создание приложения, конфиг, подключение БД, регистрация blueprints.
- `app/db.py` — подключение к SQLite, инициализация схемы, сиды, runtime-миграции.
- `app/schema.sql` — полная схема БД с нуля.
- `app/utils.py` — декораторы доступа, валидации, работа с именами файлов.
- `app/product_service.py` — пример вынесения бизнес-логики из route в отдельный helper/service.
- `app/routes/*.py` — серверная логика по разделам.
- `app/templates/` — HTML и Jinja-шаблоны.
- `app/static/css/styles.css` — все стили проекта.
- `app/static/js/` — клиентская логика.
- `app/static/uploads/` — загруженные пользователями файлы.
- `instance/hackathon.sqlite` — локальная SQLite база.

## 3. Что происходит при старте приложения

Главный файл старта:

```python
# run.py
from app import create_app

app = create_app()
```

Настоящая инициализация находится в `app/__init__.py`.

Там делается несколько важных вещей:

1. Создается Flask app.
2. В конфиг кладутся:
   - `SECRET_KEY`
   - путь к SQLite
   - папка загрузок
   - лимит размера файла
3. Создаются директории для загрузок.
4. Подключается БД через `db.init_app(app)`.
5. Вызывается `db.ensure_runtime_schema()`.
6. На каждый request подгружается текущий пользователь в `g.user`.
7. Регистрируются все blueprints.
8. Подключается обработчик `404`.

Ключевая мысль:

- если новая страница не зарегистрирована в `create_app()`, Flask ее не увидит;
- если новая таблица есть только в `schema.sql`, но нет миграции для уже существующей БД, старая база может сломаться;
- если пользователь нужен в шаблоне или route, он уже доступен как `g.user`.

## 4. Архитектурные правила текущего проекта

Это важно соблюдать, чтобы код был в одном стиле с остальным проектом.

### 4.1. Blueprints по фичам

Почти каждая фича лежит в своем файле внутри `app/routes/`.

Примеры:

- `auth.py` — авторизация
- `products.py` — каталог и карточки товаров
- `cart.py` — корзина
- `profile.py` — профиль
- `calendar.py` — календарь
- `table.py` — простая CRUD-таблица
- `stats.py` — статистика
- `chat.py` — чат

Стандартный шаблон route-файла:

```python
from flask import Blueprint, render_template

bp = Blueprint("feature_name", __name__, url_prefix="/feature")


@bp.route("/")
def index():
    return render_template("feature/index.html")
```

`Blueprint("feature_name", ...)` влияет на `url_for(...)`.

Пример:

- blueprint: `"calendar"`
- функция: `index`
- вызов: `url_for("calendar.index")`

### 4.2. Raw SQL вместо ORM

В проекте нет SQLAlchemy. Здесь используется обычный SQL:

```python
db = get_db()
rows = db.execute("SELECT * FROM table_name").fetchall()
```

Это значит:

- все таблицы и поля вы пишете вручную;
- все `SELECT`, `INSERT`, `UPDATE`, `DELETE` тоже пишутся вручную;
- нужно самому следить, что название поля в SQL совпадает с шаблоном и формой.

### 4.3. Текущий пользователь лежит в `g.user`

Перед каждым запросом приложение делает это:

- читает `session["user_id"]`;
- если пользователь найден, кладет запись о нем в `g.user`;
- если нет, `g.user = None`.

Поэтому:

- в route можно писать `if g.user is None`;
- в шаблоне можно делать `{% if g.user %}`.

### 4.4. Защита страниц через декораторы

В `app/utils.py` уже есть:

- `login_required`
- `roles_required(*roles)`

Использование:

```python
@bp.route("/")
@login_required
def index():
    ...
```

Или:

```python
@bp.route("/admin-only")
@roles_required("admin")
def admin_only():
    ...
```

### 4.5. После `POST` обычно идет `redirect`

Это уже используется почти везде и это правильно.

Паттерн:

```python
if request.method == "POST":
    ...
    db.commit()
    flash("Сохранено.", "success")
    return redirect(url_for("feature.index"))

return render_template(...)
```

Почему так:

- не будет повторной отправки формы при `F5`;
- пользователю проще видеть итоговое состояние;
- это стандартная схема Flask-приложений.

### 4.6. Общий layout задает `base.html`

Почти все шаблоны делают:

```html
{% extends "base.html" %}
```

Главные блоки:

- `{% block title %}` — заголовок вкладки
- `{% block content %}` — тело страницы
- `{% block scripts %}` — JS только для этой страницы

### 4.7. Стили и JS без сборщика

Здесь нет `npm`, `vite`, `webpack`.

Значит:

- CSS пишется прямо в `app/static/css/styles.css`;
- JS пишется прямо в `app/static/js/*.js`;
- скрипт подключается из шаблона страницы.

### 4.8. Загрузки файлов идут в `app/static/uploads`

Файлы сохраняются в подпапки:

- `uploads/products`
- `uploads/forms`
- `uploads/topups`

Если добавляете новый тип загрузок, обычно нужно:

1. создать новую подпапку;
2. добавить `os.makedirs(...)` в `create_app()`;
3. написать код сохранения файла;
4. хранить путь в БД в формате вроде `uploads/notes/file.png`.

## 5. Какие модули лучше изучить как примеры

Если нужно быстро понять проект, изучайте фичи в таком порядке:

### Самые простые

- `app/routes/advertisements.py`
  Показывает, как выглядит самая простая страница без сложной логики.

- `app/routes/main.py`
  Показывает, как собрать страницу из нескольких SQL-запросов.

### Хорошие примеры обычного CRUD

- `app/routes/table.py`
  Самый простой CRUD:
  - список
  - добавление
  - редактирование
  - удаление

- `app/routes/calendar.py`
  CRUD с датами и разными страницами внутри одной фичи.

### Примеры сложнее

- `app/routes/products.py`
  Большой CRUD с фильтрами, тегами, категориями, файлами, отзывами.

- `app/product_service.py`
  Показывает, как вынести помощь по валидации и загрузке файлов из route.

- `app/routes/profile.py`
  Показывает:
  - несколько отдельных POST-экшенов на одной странице;
  - загрузку изображения;
  - проверку пароля;
  - изменение данных пользователя.

- `app/routes/admin.py`
  Показывает:
  - проверку ролей;
  - панель администратора;
  - формы для управления чужими данными.

- `app/routes/stats.py`
  Показывает:
  - JSON endpoint;
  - генерацию изображения через Matplotlib;
  - экспорт CSV.

- `app/routes/chat.py`
  Показывает:
  - работу с несколькими пользователями;
  - запросы с unread/read логикой;
  - длинные SQL-запросы, которые все еще можно держать в route.

## 6. Карта текущих URL

Это полезно, чтобы понимать стиль именования.

| Фича | Префикс | Что делает |
| --- | --- | --- |
| `main` | `/` | Главная |
| `auth` | `/auth` | Логин, регистрация, logout |
| `products` | `/products` | Каталог, карточка, мои товары |
| `cart` | `/cart` | Корзина и checkout |
| `profile` | `/profile` | Профиль и пополнение |
| `admin` | `/admin` | Админка |
| `calendar` | `/calendar` | Календарь |
| `table` | `/table` | Демонстрационная таблица |
| `stats` | `/stats` | Графики и экспорт |
| `forms` | `/forms` | Пример форм и загрузок |
| `chat` | `/chat` | Чат |
| `advertisements` | `/advertisements` | Простая рекламная страница |

Полный список route удобно смотреть командой:

```bash
python -m flask --app run.py routes
```

## 7. Как строится одна фича

Почти любая новая страница в этом проекте состоит из 4-7 частей.

Минимальный набор:

1. Route-файл или новый route внутри существующего файла.
2. HTML-шаблон.
3. Ссылка в навигации, если страница должна быть доступна из меню.
4. SQL-запросы, если страница работает с данными.

Часто дополнительно:

5. Новая таблица или поля в БД.
6. Стили в `styles.css`.
7. JS в `static/js`.
8. Helper/service, если логика разрастается.

## 8. Как добавить простую страницу без БД

Предположим, нужна страница `/about`.

### Шаг 1. Создать route

Файл `app/routes/about.py`:

```python
from flask import Blueprint, render_template

bp = Blueprint("about", __name__, url_prefix="/about")


@bp.route("/")
def index():
    return render_template("about.html")
```

### Шаг 2. Зарегистрировать blueprint

В `app/__init__.py`:

```python
from .routes import about
...
app.register_blueprint(about.bp)
```

### Шаг 3. Создать шаблон

Файл `app/templates/about.html`:

```html
{% extends "base.html" %}

{% block title %}О проекте{% endblock %}

{% block content %}
<section class="section">
    <h1>О проекте</h1>
    <p>Это простая страница без БД.</p>
</section>
{% endblock %}
```

### Шаг 4. Добавить ссылку в меню

В `app/templates/base.html`:

```html
<a href="{{ url_for('about.index') }}">О проекте</a>
```

После этого страница уже работает.

## 9. Как добавить полноценную рабочую страницу с функцией

Ниже самый важный раздел. Здесь показан полный шаблон новой фичи.

Пример фичи:

- страница `Мои заметки`;
- пользователь может добавлять заметки;
- видеть список своих заметок;
- отмечать заметку выполненной;
- удалять заметку.

Это хороший учебный пример, потому что в нем есть:

- новая таблица БД;
- защита через `login_required`;
- `GET` + `POST`;
- валидация;
- вывод данных;
- несколько действий на одной странице.

### 9.1. Что именно нужно изменить

Нужно будет затронуть:

1. `app/schema.sql`
2. `app/db.py`
3. `app/routes/notes.py`
4. `app/__init__.py`
5. `app/templates/notes/index.html`
6. `app/templates/base.html`
7. `app/static/css/styles.css`

### 9.2. Шаг 1. Добавить таблицу в `app/schema.sql`

Для новой установки проекта таблица должна создаваться сразу.

Пример:

```sql
DROP TABLE IF EXISTS notes;

CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    is_done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

Важно:

- если таблица зависит от `users`, создавайте ее после `users`;
- если делаете `init-db`, старые данные сотрутся, потому что схема начинается с `DROP TABLE IF EXISTS`.

### 9.3. Шаг 2. Добавить runtime-миграцию в `app/db.py`

Это нужно для уже существующей локальной базы.

Внутри `ensure_runtime_schema()` добавьте:

```python
db.executescript(
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL DEFAULT '',
        is_done INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
)
```

Если проект уже запущен на существующей БД, этого часто достаточно, чтобы новая таблица появилась без полного сброса базы.

### 9.4. Шаг 3. При желании добавить demo-данные

Если хотите, чтобы после `init-db` у страницы были стартовые записи, добавьте их в `seed_db(db)`.

Пример:

```python
db.executemany(
    """
    INSERT INTO notes (user_id, title, body, is_done)
    VALUES (?, ?, ?, ?)
    """,
    [
        (1, "Проверить главную", "Посмотреть блоки и навигацию", 0),
        (2, "Подготовить презентацию", "Собрать 5 слайдов", 1),
    ],
)
```

Это не обязательно для рабочей фичи, но полезно для демо.

### 9.5. Шаг 4. Создать route-файл `app/routes/notes.py`

Полный рабочий пример:

```python
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.db import get_db
from app.utils import login_required


bp = Blueprint("notes", __name__, url_prefix="/notes")


def parse_note_form():
    return {
        "title": request.form.get("title", "").strip(),
        "body": request.form.get("body", "").strip(),
    }


def validate_note(payload):
    if not payload["title"]:
        return "Введите заголовок заметки."
    if len(payload["title"]) > 120:
        return "Заголовок должен быть не длиннее 120 символов."
    return None


@bp.route("/")
@login_required
def index():
    notes = get_db().execute(
        """
        SELECT id, title, body, is_done, created_at, updated_at
        FROM notes
        WHERE user_id = ?
        ORDER BY is_done ASC, created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("notes/index.html", notes=notes)


@bp.post("/add")
@login_required
def add():
    payload = parse_note_form()
    error = validate_note(payload)
    if error:
        flash(error, "danger")
    else:
        db = get_db()
        db.execute(
            """
            INSERT INTO notes (user_id, title, body)
            VALUES (?, ?, ?)
            """,
            (g.user["id"], payload["title"], payload["body"]),
        )
        db.commit()
        flash("Заметка добавлена.", "success")
    return redirect(url_for("notes.index"))


@bp.post("/<int:note_id>/toggle")
@login_required
def toggle(note_id):
    db = get_db()
    note = db.execute(
        "SELECT id, is_done FROM notes WHERE id = ? AND user_id = ?",
        (note_id, g.user["id"]),
    ).fetchone()
    if note is None:
        flash("Заметка не найдена.", "danger")
    else:
        db.execute(
            """
            UPDATE notes
            SET is_done = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
            """,
            (0 if note["is_done"] else 1, note_id, g.user["id"]),
        )
        db.commit()
        flash("Статус заметки обновлен.", "success")
    return redirect(url_for("notes.index"))


@bp.post("/<int:note_id>/delete")
@login_required
def delete(note_id):
    db = get_db()
    db.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, g.user["id"]),
    )
    db.commit()
    flash("Заметка удалена.", "info")
    return redirect(url_for("notes.index"))
```

Что здесь важно:

- `Blueprint("notes", ...)` создает namespace `notes.*`;
- `@login_required` закрывает страницу от гостей;
- `g.user["id"]` гарантирует, что пользователь работает только со своими данными;
- `parse_note_form()` и `validate_note()` делают код чище;
- после каждой записи в БД нужен `db.commit()`;
- после каждого `POST` идет `redirect(...)`.

### 9.6. Шаг 5. Зарегистрировать новый blueprint

В `app/__init__.py`:

```python
from .routes import ..., notes, ...
...
app.register_blueprint(notes.bp)
```

Если забыть этот шаг:

- файл будет существовать;
- route будет написан правильно;
- но Flask не увидит URL вообще.

### 9.7. Шаг 6. Создать шаблон `app/templates/notes/index.html`

Полный пример:

```html
{% extends "base.html" %}

{% block title %}Мои заметки{% endblock %}

{% block content %}
<section class="section">
    <div class="section-head">
        <div>
            <p class="eyebrow">Личный раздел</p>
            <h1>Мои заметки</h1>
        </div>
    </div>

    <form method="post" action="{{ url_for('notes.add') }}" class="form-card notes-form">
        <label>Заголовок
            <input type="text" name="title" maxlength="120" required>
        </label>
        <label>Описание
            <textarea name="body" rows="4" placeholder="Необязательно"></textarea>
        </label>
        <button type="submit">Добавить заметку</button>
    </form>

    <div class="notes-grid">
        {% for note in notes %}
            <article class="card note-card {% if note.is_done %}done{% endif %}">
                <div class="card-body">
                    <div class="card-row">
                        <h2>{{ note.title }}</h2>
                        <span class="pill">
                            {% if note.is_done %}Выполнено{% else %}В работе{% endif %}
                        </span>
                    </div>

                    {% if note.body %}
                        <p>{{ note.body }}</p>
                    {% endif %}

                    <div class="muted small-text">
                        Создано: {{ note.created_at }}
                    </div>

                    <div class="button-group note-actions">
                        <form method="post" action="{{ url_for('notes.toggle', note_id=note.id) }}" class="inline-form">
                            <button type="submit" class="button secondary">
                                {% if note.is_done %}Вернуть в работу{% else %}Отметить выполненной{% endif %}
                            </button>
                        </form>

                        <form
                            method="post"
                            action="{{ url_for('notes.delete', note_id=note.id) }}"
                            class="inline-form"
                            data-confirm-message="Удалить заметку «{{ note.title }}»?"
                            data-confirm-title="Удалить заметку?"
                            data-confirm-variant="danger"
                            data-confirm-confirm-label="Удалить"
                        >
                            <button type="submit" class="button secondary">Удалить</button>
                        </form>
                    </div>
                </div>
            </article>
        {% else %}
            <div class="empty-state">
                <h2>Заметок пока нет</h2>
                <p>Создайте первую заметку через форму выше.</p>
            </div>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

Что здесь важно:

- шаблон наследуется от `base.html`;
- форма отправляется на `url_for('notes.add')`;
- список строится через `{% for %}`;
- удаление идет отдельной формой, а не ссылкой;
- подтверждение удаления уже поддерживается глобальным `modals.js`, потому что используются `data-confirm-*`.

### 9.8. Шаг 7. Добавить ссылку в меню

В `app/templates/base.html` можно добавить:

```html
{% if g.user %}
    <a href="{{ url_for('notes.index') }}">Заметки</a>
{% endif %}
```

Если страница доступна только авторизованным, логично показывать ссылку только при наличии `g.user`.

### 9.9. Шаг 8. Добавить стили в `app/static/css/styles.css`

Минимальный пример:

```css
.notes-grid {
    display: grid;
    gap: 1rem;
}

.note-card.done {
    opacity: 0.8;
    border: 1px solid var(--line);
}

.note-actions {
    margin-top: 1rem;
}
```

Лучше придерживаться текущего стиля проекта:

- использовать понятные классы с префиксом фичи, например `.notes-*`;
- не писать inline-style в HTML;
- не ломать существующие глобальные классы вроде `.section`, `.card`, `.button`.

### 9.10. Шаг 9. Применить изменения к базе

Есть два сценария.

#### Если это локальная демо-база и данные не жалко

```bash
python -m flask --app run.py init-db
```

Это пересоздаст всю базу по `schema.sql`.

#### Если это существующая база и данные терять нельзя

Не делайте `init-db`.

Достаточно:

1. обновить `ensure_runtime_schema()` в `app/db.py`;
2. перезапустить приложение.

### 9.11. Шаг 10. Проверить руками

Чеклист:

1. Открывается `/notes/`.
2. Гость перекидывается на логин.
3. Авторизованный пользователь видит страницу.
4. Пустая заметка не сохраняется.
5. Валидная заметка сохраняется.
6. После сохранения виден `flash`.
7. Можно переключить статус заметки.
8. Можно удалить заметку.
9. Один пользователь не видит заметки другого.

Если все это работает, значит вы действительно добавили новую полноценную фичу.

## 10. Как понять, нужно ли менять БД

Задайте себе один вопрос:

"Нужно ли сохранять новые данные между перезагрузками?"

Если нет:

- можно обойтись только route + template + JS.

Если да:

- почти наверняка нужна новая таблица или новые поля.

Примеры:

- новая статичная страница "О нас" — БД не нужна;
- фильтр на уже существующем каталоге — БД обычно не нужна;
- новая форма обратной связи с сохранением заявок — нужна БД;
- новые аватары пользователей — нужен столбец или отдельная таблица;
- новые загружаемые файлы — нужен путь к файлу в БД.

## 11. Как безопасно менять существующую страницу

Самая частая задача в жизни проекта — не создать новую страницу, а расширить уже имеющуюся.

Лучший порядок такой:

1. Найдите route-файл фичи.
2. Найдите связанный шаблон.
3. Посмотрите, откуда берутся данные.
4. Измените SQL.
5. Измените обработку формы.
6. Измените HTML.
7. Если надо, добавьте стили и JS.
8. Проверьте сценарий руками.

### Пример мышления

Если нужно добавить новое поле в товар, например `sku`, вам нужно проверить:

1. есть ли поле в БД;
2. читает ли его `SELECT`;
3. передает ли route значение в шаблон;
4. есть ли `<input name="sku">` в форме;
5. сохраняется ли `sku` в `INSERT` и `UPDATE`;
6. выводится ли `sku` на карточке товара;
7. учитывает ли это админка и форма редактирования.

Очень частая ошибка джуна:

- добавить поле в HTML;
- забыть обновить `INSERT`/`UPDATE`;
- удивляться, почему значение "не сохраняется".

## 12. Когда выносить логику в service/helper

Сейчас в проекте есть `app/product_service.py`.

Это хороший сигнал, когда нужно выносить код:

- одна и та же логика используется в двух route-файлах;
- route стал слишком длинным;
- в нем много валидации, нормализации и работы с файлами;
- хочется переиспользовать функции.

Что разумно выносить:

- парсинг формы;
- валидацию;
- сохранение файлов;
- вычисление списка опций;
- нормализацию данных.

Что обычно можно оставлять в route:

- сам `GET/POST` flow;
- `flash`, `redirect`, `render_template`;
- SQL, если он небольшой и касается только этой фичи.

## 13. Как добавлять формы правильно

Почти все формы в проекте строятся одинаково.

### Сервер

В route:

```python
if request.method == "POST":
    value = request.form.get("value", "").strip()
    ...
```

Или для отдельного POST endpoint:

```python
@bp.post("/add")
def add():
    ...
```

### HTML

```html
<form method="post">
    <input type="text" name="value">
    <button type="submit">Сохранить</button>
</form>
```

### Если есть загрузка файла

Нужно обязательно:

```html
<form method="post" enctype="multipart/form-data">
```

Иначе файл просто не придет в `request.files`.

### Валидация

Сначала валидируйте, потом пишите в БД:

```python
error = None
if not value:
    error = "Введите значение."

if error:
    flash(error, "danger")
else:
    ...
```

## 14. Как добавлять загрузку файлов

В проекте уже есть готовые примеры:

- `profile.py` — загрузка чека пополнения;
- `forms.py` — загрузка картинки и файла;
- `products.py` — загрузка изображения товара.

Типовой паттерн:

1. взять файл из `request.files`;
2. проверить расширение;
3. сгенерировать безопасное уникальное имя;
4. сохранить файл в `app/static/uploads/...`;
5. записать относительный путь в БД.

Пример сохранения пути:

```python
receipt_path = f"uploads/topups/{filename}"
```

Потом в шаблоне:

```html
{{ url_for('static', filename=topup.receipt_path) }}
```

Если добавляете новый тип загрузок:

1. создайте подпапку;
2. добавьте `os.makedirs(...)` в `create_app()`;
3. решите, какие расширения разрешены;
4. сохраните путь в БД.

## 15. Как подключать JS на страницу

Текущий проект использует простой подход:

- общий JS загружается в `base.html`;
- page-specific JS подключается в `{% block scripts %}`.

Пример:

```html
{% block scripts %}
<script src="{{ url_for('static', filename='js/stats.js') }}"></script>
{% endblock %}
```

Что уже есть из общих скриптов:

- `theme.js` — тема сайта
- `modals.js` — confirm/dialog
- `image-preview.js` — предпросмотр картинок

Что важно:

- привязывайте JS к `data-*` атрибутам или понятным классам;
- не завязывайтесь на случайные DOM-структуры;
- если логика нужна только одной странице, не кладите ее в общий глобальный скрипт.

## 16. Как использовать уже готовые возможности UI

В проекте уже есть переиспользуемые паттерны.

### 16.1. Flash-сообщения

В route:

```python
flash("Сохранено.", "success")
flash("Ошибка.", "danger")
flash("Удалено.", "info")
flash("Нужно войти.", "warning")
```

Выводить вручную их не нужно. `base.html` уже включает:

```html
{% include "components/flash.html" %}
```

### 16.2. Подтверждение действий

Если форме нужно подтверждение, можно использовать уже существующий modal-механизм:

```html
<form
    method="post"
    data-confirm-message="Удалить запись?"
    data-confirm-title="Подтверждение"
    data-confirm-variant="danger"
    data-confirm-confirm-label="Удалить"
>
```

Это подхватит `app/static/js/modals.js`.

### 16.3. Предпросмотр картинки

Если хотите открыть изображение в модалке:

```html
<button
    type="button"
    data-preview-src="{{ url_for('static', filename=item.image_path) }}"
    data-preview-title="Название"
>
    Открыть
</button>
```

Это подхватит `app/static/js/image-preview.js`.

### 16.4. Компоненты

Если кусок HTML повторяется, лучше вынести его в `templates/components/`.

Уже есть пример:

- `components/product_card.html`

Подключение:

```html
{% include "components/product_card.html" %}
```

## 17. Как добавлять JSON endpoint или данные для JS

Если страница требует не только HTML, но и данные для JavaScript, смотрите на `stats.py`.

Пример:

```python
@bp.route("/data")
@login_required
def data():
    return jsonify({...})
```

Когда это полезно:

- графики;
- автообновление;
- легкая асинхронщина без полной SPA;
- маленькие виджеты.

Но если можно обойтись обычным `render_template(...)`, лучше начинать с него. Для этого проекта это более естественный путь.

## 18. Как добавлять роль-зависимую страницу

Если страница только для админа:

```python
@bp.route("/")
@roles_required("admin")
def index():
    ...
```

Если для нескольких ролей:

```python
@roles_required("manager", "admin")
```

В шаблоне можно скрывать ссылку так:

```html
{% if g.user and g.user.role == 'admin' %}
    <a href="{{ url_for('admin.dashboard') }}">Админ</a>
{% endif %}
```

Важно:

- скрытая ссылка в меню не заменяет защиту route;
- проверка роли обязательно должна быть и на сервере.

## 19. Частые ошибки при доработке

### Ошибка 1. Route написан, но URL не открывается

Проверьте:

- зарегистрирован ли blueprint в `app/__init__.py`;
- правильный ли `url_prefix`;
- правильный ли endpoint в `url_for(...)`.

### Ошибка 2. Шаблон не видит переменную

Скорее всего:

- route не передал ее в `render_template(...)`;
- название переменной в шаблоне не совпадает с Python.

### Ошибка 3. Данные не сохраняются в БД

Проверьте:

- был ли `db.commit()`;
- сработала ли валидация;
- правильные ли имена полей формы;
- правильный ли SQL.

### Ошибка 4. `sqlite3.OperationalError: no such table`

Почти всегда значит:

- вы добавили таблицу в `schema.sql`;
- но не пересоздали БД и не добавили `ensure_runtime_schema()`.

### Ошибка 5. Файл не загружается

Проверьте:

- есть ли `enctype="multipart/form-data"`;
- правильный ли `request.files.get(...)`;
- разрешено ли расширение файла;
- существует ли папка назначения.

### Ошибка 6. Кнопка удаления сделана ссылкой

Удаление лучше делать через `POST`, а не через `<a href="...">`.

В этом проекте destructive actions уже идут через формы:

- удаление строки;
- удаление товара;
- удаление события.

Так и продолжайте.

## 20. Как быстро искать нужное место в коде

Полезные команды:

```bash
python -m flask --app run.py routes
```

Показывает все URL и endpoint.

```bash
rg "Blueprint\\(" app/routes
```

Показывает все blueprints.

```bash
rg "url_for\\(" app/templates
```

Показывает, как страницы связаны между собой.

```bash
rg "flash\\(" app/routes
```

Показывает паттерны обратной связи пользователю.

```bash
rg "request.files" app/routes
```

Показывает, где и как сделаны загрузки.

## 21. Практический алгоритм для джуна

Если завтра вам скажут:

"Сделай новую страницу с формой, сохранением и списком данных"

действуйте так:

1. Найдите самый похожий модуль.
   Лучше всего начать с `table.py`, `forms.py` или `profile.py`.
2. Решите, нужны ли новые данные в БД.
3. Если нужны, добавьте таблицу или поля:
   - в `schema.sql`
   - в `ensure_runtime_schema()`
4. Создайте новый blueprint в `app/routes/`.
5. Зарегистрируйте blueprint в `app/__init__.py`.
6. Сделайте `GET` route для страницы.
7. Сделайте `POST` route для действия.
8. Создайте шаблон в `app/templates/...`.
9. Добавьте ссылку в меню, если нужно.
10. Добавьте стили и JS, если нужно.
11. Проверьте руками весь сценарий.

Если не знаете, куда положить код, используйте правило:

- route и flow — в `app/routes/...`;
- общие helper-функции — в `app/utils.py` или отдельный `*_service.py`;
- HTML — в `app/templates/...`;
- CSS — в `app/static/css/styles.css`;
- JS — в `app/static/js/...`;
- структура данных — в `app/schema.sql` и `app/db.py`.

## 22. Финальный чеклист перед завершением задачи

Перед тем как считать страницу готовой, проверьте:

### Сервер

- blueprint зарегистрирован;
- route открывается;
- защита доступа работает;
- SQL не падает;
- `db.commit()` стоит там, где нужно.

### Шаблон

- страница наследуется от `base.html`;
- все ссылки сделаны через `url_for(...)`;
- формы имеют правильный `method`;
- файл-форма имеет `enctype="multipart/form-data"`, если нужно.

### База

- таблица или поле есть в `schema.sql`;
- для старой БД есть совместимое изменение в `ensure_runtime_schema()`.

### UI

- success/error сообщения видны;
- кнопки не ломают layout;
- страница выглядит нормально и на пустом состоянии;
- destructive actions идут через `POST`.

### Поведение

- happy path работает;
- пустые/битые данные не ломают страницу;
- пользователь не может менять чужие данные;
- после действий понятный `redirect`.

## 23. Короткий вывод

Чтобы расширять этот проект, нужно мыслить не "страницей", а связкой:

- маршрут;
- шаблон;
- данные;
- валидация;
- доступ;
- стили;
- иногда JS.

Если придерживаться текущих паттернов проекта, то почти любая новая фича делается по одной и той же схеме:

1. придумали данные;
2. добавили SQL;
3. сделали route;
4. сделали шаблон;
5. подключили ссылку;
6. проверили руками.

Если сомневаетесь, с чего копировать структуру:

- простая CRUD-страница: смотрите `app/routes/table.py`;
- форма с файлами: смотрите `app/routes/forms.py` и `app/routes/profile.py`;
- сложная фича с множеством сущностей: смотрите `app/routes/products.py` и `app/product_service.py`;
- доступ по ролям: смотрите `app/routes/admin.py`;
- JS + данные для графиков: смотрите `app/routes/stats.py` и `app/static/js/stats.js`.

Это самый короткий путь начать вносить изменения уверенно и без хаоса.
