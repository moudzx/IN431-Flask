"""Supplied SQLite teaching migrations. Do not replace these with create_all.

One file is upgraded in place. This narrowly scoped runner is for this lab.
Use a reviewed migration system such as Alembic for a general deployment workflow.
"""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import uuid
from .extensions import db

MIGRATIONS = {
    1: [
        """CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(120) NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            CONSTRAINT ck_task_title CHECK (length(title) BETWEEN 3 AND 120),
            CONSTRAINT ck_task_done CHECK (done IN (0, 1))
        )""",
    ],
    2: [
        """CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            CONSTRAINT ck_project_name CHECK (length(name) BETWEEN 3 AND 100)
        )""",
        """ALTER TABLE tasks ADD COLUMN project_id INTEGER
            REFERENCES projects(id) ON DELETE SET NULL""",
    ],
    3: [
        """CREATE TABLE project_details (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL UNIQUE
                REFERENCES projects(id) ON DELETE CASCADE,
            description VARCHAR(500) NOT NULL DEFAULT '',
            CONSTRAINT ck_details_description CHECK (length(description) <= 500)
        )""",
    ],
    4: [
        """CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(40) NOT NULL UNIQUE,
            CONSTRAINT ck_tag_name CHECK (length(name) BETWEEN 2 AND 40)
        )""",
        """CREATE TABLE task_tags (
            task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (task_id, tag_id)
        )""",
    ],
}

def check_mapping(target):
    from . import models
    if not {"id", "title", "done"}.issubset(models.Task.__table__.columns.keys()):
        raise ValueError("Complete A1 before initializing the database")
    if target >= 2:
        if not hasattr(models, "Project") or not hasattr(models.Task, "project"):
            raise ValueError("Complete B1 model mappings before upgrade --to 2")
        if "project_id" not in models.Task.__table__.columns:
            raise ValueError("Add Task.project_id in B1")
    if target >= 3:
        if not hasattr(models, "ProjectDetails") or not hasattr(models.Project, "details"):
            raise ValueError("Complete C1 model mappings before upgrade --to 3")
    if target >= 4:
        if not hasattr(models, "Tag") or not hasattr(models.Task, "tags"):
            raise ValueError("Complete D1 model mappings before upgrade --to 4")

def upgrade_schema(target):
    if db.engine.dialect.name != "sqlite":
        raise ValueError("This supplied teaching runner supports SQLite only")
    if target not in MIGRATIONS:
        raise ValueError("Choose a schema version from 1 to 4")
    check_mapping(target)
    db.session.remove()
    pooled = db.engine.raw_connection()
    connection = pooled.driver_connection
    backup = None
    try:
        current = connection.execute("PRAGMA user_version").fetchone()[0]
        if target < current:
            raise ValueError("Downgrades are not part of this lab")
        if target == current:
            return {"version": current, "backup": None, "changed": False}
        if connection.in_transaction:
            raise ValueError("Stop active database work before upgrading")
        # Keep a recoverable copy of an existing schema before changing it.
        database = db.engine.url.database
        if current and database and database != ":memory:":
            source = Path(database)
            backup_dir = source.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            backup = backup_dir / (source.stem + f".v{current}.before-v{target}."
                                    + stamp + "." + uuid.uuid4().hex[:6] + ".db")
            with sqlite3.connect(backup) as destination:
                connection.backup(destination)
        # Explicit BEGIN includes SQLite DDL in this transaction.
        connection.execute("BEGIN IMMEDIATE")
        try:
            for version in range(current + 1, target + 1):
                for statement in MIGRATIONS[version]:
                    connection.execute(statement)
                connection.execute("PRAGMA user_version = " + str(version))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        return {"version": target, "backup": str(backup) if backup else None,
                "changed": True}
    finally:
        pooled.close()
