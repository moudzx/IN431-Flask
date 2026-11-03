# IN432 Advanced Web Technologies: Labs

Hands-on lab work for **IN432 – Advanced Web Technologies** (Master M1, Computer Science, Lebanese University). The labs build up one idea step by step: from a Flask page that serves JSON, to a validated CRUD API, to a database-backed API with related data.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## Contents

| Lab | Topic | Project | What you practice |
|---|---|---|---|
| [Lab 1](lab1-introduction/) | Python + Flask + Fetch | **Campus Support Mini** | Static HTML page, browser `fetch`, Flask routes, JSON responses, query-string validation, HTTP status codes |
| [Lab 2](lab2-flask/) | Flask CRUD | **Task API** | `POST` / `PATCH` / `DELETE`, input validation, error handling, `Location` headers, Blueprints, `PUT` vs `PATCH` |
| [Lab 3](lab3-sqlalchemy/) | Flask + SQLAlchemy | **Task Manager** | ORM models, persistence, one-to-many (projects), one-to-one (project details), many-to-many (tags), transactions, schema upgrades |

Each lab folder contains the course handout (PDF) and a starter project with its own README, `requirements.txt` and checker scripts.

## Lab details

### Lab 1: Campus Support Mini
A small full-stack app showing fictional campus support tickets. A browser form calls `GET /api/tickets?status=...`, Flask validates the filter and returns JSON, and the page rebuilds the list.

| Request | Result |
|---|---|
| `GET /api/health` | `200` `{"status":"ok"}` |
| `GET /api/tickets` | `200`, 3 tickets |
| `GET /api/tickets?status=OPEN` | `200`, 2 tickets |
| `GET /api/tickets?status=UNKNOWN` | `400` JSON error |

Tickets are kept in memory and reset on restart, which motivates the database work in Lab 3.

```bash
cd lab1-introduction/campus-support-mini
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```
Open http://127.0.0.1:5000/

### Lab 2: Task API (Flask CRUD)
Follow Lina as she creates a task, completes it, sends a rejected invalid update, and deletes it. The starter supplies the app structure; you complete validation and the `POST`, `PATCH` and `DELETE` handlers (marked `TODO`). Responses use `501` until an exercise is implemented.

```bash
cd lab2-flask/IN432_Session2_Starter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python python_warmup.py                      # Python warm-up
python -m flask --app task_api run --debug   # Terminal A
python api_client.py GET /api/health         # Terminal B
python check_validation.py                   # validator checks
python verify_api.py                         # full API checks
```
The `exercises/` folder has independent observers for Blueprints and `PUT` vs `PATCH`.

### Lab 3: Task Manager (Flask + SQLAlchemy)
One evolving application with a single SQLite database (`instance/task_manager.db`), built in five parts:

| Part | Focus |
|---|---|
| A | Map `Task`, public dictionary, persisted create / list / update / delete |
| B | `Project` and a nullable foreign key on tasks |
| C | Optional one-to-one `ProjectDetails` with `PUT` |
| D | `Tag`, association table, attach and detach |
| E | Joined reports, counts, multi-object transactions |

The database evolves with CLI commands that apply specific SQLite teaching migrations and back up the database first (this is not Flask-Migrate; use Alembic for production work).

```bash
cd lab3-sqlalchemy/IN432_Session5_Student_Starter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python -m unittest checks.SetupChecks -v
python -m flask --app task_api init-db
python -m flask --app task_api run --debug

# At the matching milestones only:
python -m flask --app task_api upgrade-db --to 2
python -m flask --app task_api upgrade-db --to 3
python -m flask --app task_api upgrade-db --to 4
python -m flask --app task_api db-info
```
See `CHECKPOINTS.md`, `EVIDENCE_TEMPLATE.md` and `PYTHON_GUIDE.md` inside the starter.


## Course

**IN432 – Advanced Web Technologies**
Lebanese University, Master M1 Computer Science
Instructor: Dr. Zaher Yamak
