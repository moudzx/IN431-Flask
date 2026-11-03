# IN432 Session 5 one project lab

Build the same Task Manager application from start to finish.
Use one folder, one task_api package and one working database:
instance/task_manager.db. Keep the tasks you create in part A for every later part.
No earlier lab or starter is required.

## Setup

Open a terminal in this folder next to requirements.txt.
Windows Command Prompt:

    python -m venv .venv
    .venv\Scripts\activate.bat
    python -m pip install -r requirements.txt

macOS / Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

With this environment active:

    python -m unittest checks.SetupChecks -v

Two checks pass in the initial starter. Complete the exercises in the Word lab.
Use Python 3.10 or later. PYTHON_GUIDE.md explains the syntax used.

## Progress in the same files

- A1 and A2: map Task and define the base public dictionary.
- A3 to A6: create, list, update and delete persisted tasks.
- B1 and B2: add Project, Task.project_id, navigation and assignment.
- C1 and C2: add one optional ProjectDetails and its PUT operation.
- D1 to D3: add Tag, the association table, attach and detach.
- E1 to E3: join reports, counts and a transaction with several objects.

The marked later model regions are initially empty. Add classes when the handout
introduces them. In C1 add the details relationship inside your Project class.
Keep all part A CRUD methods. Extend the same Task.to_dict as fields are added.
There is no second application and no completed CRUD copy to switch to.

## Database evolution

Complete and check A1 before the first initialization:

    python -m flask --app task_api init-db

This creates schema version 1 with only tasks. After each later mapping exercise,
STOP the server using Ctrl+C, run the matching upgrade and restart it:

    python -m flask --app task_api upgrade-db --to 2
    python -m flask --app task_api upgrade-db --to 3
    python -m flask --app task_api upgrade-db --to 4

Run each command only at its matching milestone, not all at the beginning.
Version 2 adds projects and the nullable foreign key in the existing tasks table.
Version 3 adds project_details. Version 4 adds tags and task_tags.
The supplied schema.py command applies these specific SQLite teaching changes.
It keeps earlier task ids, titles and done values, and makes a backup before an
upgrade of an initialized database. db.create_all is not a replacement for it.
This is not Flask-Migrate; general production migration work can use Alembic.

    python -m flask --app task_api db-info

Keep the same database path. Do not delete or replace task_manager.db.

## Requests

Terminal A, from this same root:

    python -m flask --app task_api run --debug

Terminal B, from the same root with the same environment active:

    python api_client.py GET /api/health
    python api_client.py POST /api/tasks --json payloads/task.json

Keep real Location URLs and returned ids in EVIDENCE_TEMPLATE.md.
Use the same T1 and T2 throughout. Replace illustrative ids in commands and in
assign_project.json with your actual values.
Unfinished methods return HTTP 501; later models also report 501 until added.

## Checks

Run only the named group for the current exercise. Checks use temporary databases;
they do not change your working file. See CHECKPOINTS.md.

After A1 to A6, run:

    python -m unittest checks.SetupChecks checks.ModelChecks checks.RepresentationChecks -v
    python -m unittest checks.CreateChecks checks.ListChecks -v
    python -m unittest checks.UpdateChecks checks.DeleteChecks checks.TransactionChecks -v

After all exercises:

    python -m unittest checks -v

Do not submit .venv, instance or Python cache folders. The Flask debug server is
for this local lab. Backups remain under instance/backups for your own use.
