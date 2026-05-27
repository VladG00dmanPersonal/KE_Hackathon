import os

from flask import Flask, g, render_template, session

from . import db
from .routes import advertisements, admin, auth, calendar, cart, chat, forms, main, products, profile, stats, table


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        DATABASE=os.path.join(app.instance_path, "hackathon.sqlite"),
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads"),
        MAX_CONTENT_LENGTH=12 * 1024 * 1024,
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "topups"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "forms"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "products"), exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.ensure_runtime_schema()

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = None
        if user_id is not None:
            g.user = db.get_db().execute(
                "SELECT id, email, nickname, pending_email, role, balance, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(calendar.bp)
    app.register_blueprint(table.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(forms.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(advertisements.bp)

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template("404.html"), 404

    return app
