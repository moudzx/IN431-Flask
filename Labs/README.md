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

Each lab folder contains the course handouts (PDF) and the project for that lab with its own README, `requirements.txt` and checker scripts. **All three labs are completed and pass their checkers.**

## Repository structure

```
.
├── lab1-introduction/
│   ├── IN432_Session1.pdf
│   ├── lab1.pdf
│   └── campus-support-mini/        # Flask app + static page
├── lab2-flask/
│   ├── IN432_Session2_Flask_CRUD.pdf
│   ├── IN432_Session3_Task_Workflow_Lab.pdf
│   └── IN432_Session2_Starter/     # Task API (completed): code, checkers, evidence
└── lab3-sqlalchemy/
    ├── IN432_Session4_Flask_Database_Integration.pdf
    ├── IN432_Session5_Related_Data_with_Flask.pdf
    ├── IN432_Session5_Student_Lab.pdf
    └── IN432_Session5_Student_Starter/   # Task Manager (completed): code, checkers, evidence
```

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
Follow Lina as she creates a task, completes it, sends a rejected invalid update, and deletes it.

**Implemented**

| TODO | File | What it does |
|---|---|---|
| 1a | `task_api/validation.py` | Title must be a string; trimmed; 3 to 120 characters |
| 1b | `task_api/validation.py` | `done` must be a real boolean (`type(value) is not bool`), so `0`, `1` and `"false"` are rejected while `False` is accepted |
| 2 | `task_api/tasks.py` | `POST` validates, creates, returns `201` with a `Location` header |
| 3 | `task_api/tasks.py` | `PATCH` validates in partial mode, updates, returns `200` |
| 4 | `task_api/tasks.py` | `DELETE` returns `204` with an empty body, or `404` if missing |

Results: `check_validation.py` passes **10/10** and `verify_api.py` passes **20/20**. `evidence.txt` holds the live request sequence and `checker_output.txt` the checker output.

```bash
cd lab2-flask/IN432_Session2_Starter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python python_warmup.py                      # Python warm-up
python -m flask --app task_api run --debug   # Terminal A
python api_client.py GET /api/health         # Terminal B
python check_validation.py                   # validator checks (10/10)
python verify_api.py                         # full API checks (20/20)
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

**Implemented**

| Part | Where | Notes |
|---|---|---|
| A1, A2 | `models.py` | `title` / `done` columns; `Task.to_dict` |
| A3 to A6 | `store.py` | create, list (ordered by id), update (key-presence checks so `done=False` is applied), delete |
| B1, B2 | `models.py`, `store.py` | `Project`, nullable FK with `ON DELETE SET NULL`; assign / move / unassign, with the project looked up first so a missing id changes nothing |
| C1, C2 | `models.py`, `store.py` | one-to-one `ProjectDetails` (`uselist=False`, unique FK, `delete-orphan`); `PUT` returns `201` on create and `200` on update |
| D1 to D3 | `models.py`, `store.py` | `task_tags` association table, `Tag`; attach and detach are idempotent |
| E1, E2 | `store.py` | `LEFT OUTER JOIN` reports that keep unassigned tasks and empty projects (`COUNT(Task.id)`, not `COUNT(*)`) |
| E3 | `store.py` | project bundle in one transaction: flush the parent, add details and tasks, a single commit, rollback to `500 database_error` on failure |

Results: the full suite passes (**36/36**). `evidence.txt` has the schema upgrades and the live request sequence.

**Important:** the finished models map every table, so a fresh database must be brought to the final version before use: run `init-db`, then `upgrade-db --to 2`, `--to 3` and `--to 4`, as shown below. (When working through the handout step by step, add each mapping only at its own milestone, as the lab instructs.)

```bash
cd lab3-sqlalchemy/IN432_Session5_Student_Starter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python -m unittest checks -v                 # 36 checks

python -m flask --app task_api init-db       # schema v1
python -m flask --app task_api upgrade-db --to 2
python -m flask --app task_api upgrade-db --to 3
python -m flask --app task_api upgrade-db --to 4
python -m flask --app task_api db-info
python -m flask --app task_api run --debug
```
See `CHECKPOINTS.md`, `EVIDENCE_TEMPLATE.md` and `PYTHON_GUIDE.md` inside the starter.

## Requirements

- Python 3.10 or newer (Lab 1 runs on 3.9+)
- `pip` and `venv`
- A terminal and a code editor
- `curl` or the supplied `api_client.py` for sending requests

Pinned dependencies (Lab 3): `Flask==3.1.3`, `Flask-SQLAlchemy==3.1.1`, `SQLAlchemy==2.0.55`.

## Notes

- Each lab is self-contained. Create a separate virtual environment per project folder.
- Do not commit `.venv/`, `instance/` or `__pycache__/`.
- Lab 1 had a module-level `app.run()` that blocked `flask run`; it is now guarded by `if __name__ == "__main__":`, and the 404 for an unknown ticket id returns JSON.
- Lab 2 and Lab 3 originally shipped as starters with `TODO` blocks; the `BEGIN` / `END` markers in Lab 3 were kept so the structure still matches the handouts.

## Course

**IN432 – Advanced Web Technologies**
Lebanese University, Master M1 Computer Science
Instructor: Dr. Zaher Yamak

## License

Course materials are provided for educational use. Add a license of your choice (for example MIT for your own code) before making the repository public.
