"""Initialize or upgrade the Session 5 SQLite database to the complete schema.

Run from backend/: python setup_db.py
This preserves existing data and creates a backup on upgrades.
"""
from task_api import create_app
from task_api.schema import upgrade_schema

app = create_app()
with app.app_context():
    result = upgrade_schema(4)
    print("Schema version:", result["version"])
    print("Changed:", result["changed"])
    if result["backup"]:
        print("Backup:", result["backup"])
    from task_api.extensions import db
    print("Database:", db.engine.url.database)
