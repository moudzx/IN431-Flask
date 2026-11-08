from pathlib import Path
import click
from flask import Flask, jsonify, request
from .extensions import db
from .errors import register_error_handlers
from .routes import bp
from .schema import upgrade_schema

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///task_manager.db",
                      SQLALCHEMY_TRACK_MODIFICATIONS=False)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(bp)

    # Session 6: independent frontend server (http://127.0.0.1:5500).
    # This small CORS allow-list is an HTTP boundary configuration, not
    # a frontend import or a static-file dependency. Same Flask API as Session 5.
    allowed_frontends = {
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    }

    @app.after_request
    def cors_for_independent_frontend(response):
        origin = request.headers.get("Origin")
        if request.path.startswith("/api/") and origin in allowed_frontends:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add("Vary", "Origin")
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PATCH, PUT, DELETE, OPTIONS"
            )
        return response

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", app="task_manager", session=5)

    @app.cli.command("init-db")
    def init_db():
        # Initial schema only. Later changes use upgrade-db.
        with db.engine.connect() as connection:
            current = connection.exec_driver_sql("PRAGMA user_version").scalar_one()
        if current >= 1:
            click.echo("Already initialized; current schema version: " + str(current))
            return
        try:
            result = upgrade_schema(1)
        except Exception as error:
            raise click.ClickException(str(error))
        click.echo("Initial schema version: " + str(result["version"]))
        click.echo("Database file: " + str(db.engine.url.database))

    @app.cli.command("upgrade-db")
    @click.option("--to", "target", required=True, type=click.IntRange(1, 4))
    def upgrade_db(target):
        try:
            result = upgrade_schema(target)
        except Exception as error:
            raise click.ClickException(str(error))
        click.echo("Schema version: " + str(result["version"]))
        click.echo("Database file: " + str(db.engine.url.database))
        if result["backup"]:
            click.echo("Backup: " + result["backup"])
        if not result["changed"]:
            click.echo("Already at this version; no change made.")

    @app.cli.command("db-info")
    def db_info():
        # Read actual SQLite structure, even during a model-to-schema transition.
        with db.engine.connect() as connection:
            click.echo("Database file: " + str(db.engine.url.database))
            click.echo("Schema version: " + str(
                connection.exec_driver_sql("PRAGMA user_version").scalar_one()))
            click.echo("Foreign keys: " + str(
                connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one()))
            for table in ("tasks", "projects", "project_details", "tags", "task_tags"):
                exists = connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,)).first()
                if exists:
                    count = connection.exec_driver_sql("SELECT COUNT(*) FROM " + table).scalar_one()
                    click.echo(table + ": " + str(count) + " rows")
    return app
