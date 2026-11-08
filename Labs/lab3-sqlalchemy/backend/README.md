# Working Flask backend — same package structure as IN432 Session 5

This is the **completed** Session 5 instructor code, not the incomplete student
starter. It preserves the original files: `task_api/__init__.py`, `models.py`,
`store.py`, `routes.py`, `validation.py`, `extensions.py`, `schema.py`, and `errors.py`.
It includes task CRUD, projects, tags, relationships, reports and persistent SQLite.
The only integration change is local development CORS configuration for a separate
JavaScript frontend at `http://127.0.0.1:5500` or `http://localhost:5500`.

## First start (Python 3.10+)

Windows (Command Prompt):

    python -m venv .venv
    .venv\Scripts\activate.bat
    python -m pip install -r requirements.txt
    python setup_db.py
    python -m flask --app task_api run --debug --port 5000

macOS/Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python setup_db.py
    python -m flask --app task_api run --debug --port 5000

Once started, open http://127.0.0.1:5000/api/health.

**Note:** the supplied completed models have all Session 5 relationships. The
SQLite database must be at schema version 4. `setup_db.py` creates/upgrades
it directly to version 4 using the existing incremental migrations. It is
safe to re-run; existing data is preserved and upgraded databases receive a backup.
Do not delete `instance/task_manager.db` if it contains your Session 5 work.

## Tests

    python -m unittest smoke_test -v
    python -m unittest checks -v

Both suites use temporary databases and do not alter the working one.

## API

    GET    /api/health
    GET    /api/tasks
    GET    /api/tasks/<id>
    POST   /api/tasks                 JSON {"title":"My task"}
    PATCH  /api/tasks/<id>            JSON {"done":true} or {"title":"New title"}
    DELETE /api/tasks/<id>

Additional Session 5 endpoints include `/api/projects`, `/api/tags`,
`PUT /api/tasks/<id>/project` and reports. See `task_api/routes.py`.
The task interface uses PATCH for changing a task; there is no generic
`PUT /api/tasks/<id>` route in this API.

## Separate frontend / different machine

Backend and frontend are **independent** and start in separate terminals.
They can be served on different hosts. In the classroom, the API listens
on loopback port 5000 and HTML on loopback port 5500.

To serve across a LAN, configure Flask to listen on a reachable interface,
firewall/network access, the URL in `../frontend/config.js`, and the CORS
allow-list in `task_api/__init__.py` for the actual frontend origin.
Flask debug mode and the built-in development server are for local labs only.
