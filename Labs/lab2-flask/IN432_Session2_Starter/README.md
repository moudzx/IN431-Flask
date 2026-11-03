# IN432 Session 2 guided Python lab

Start with the English Word tutorial. This edition is for students who know
Java and C and are learning Python during the lab. All commands below are
terminal commands. Open the terminal in the folder containing requirements.txt.

1. Create an environment: `python -m venv .venv`.
2. Activate it, then install: `python -m pip install -r requirements.txt`.
3. Run the Python warm-up: `python python_warmup.py`.
4. In Terminal A, start the API: `python -m flask --app task_api run --debug`.
5. In Terminal B, activate the same environment and run:
   `python api_client.py GET /api/health` and `python verify_api.py --baseline`.

Activation: Windows Command Prompt `.venv\Scripts\activate.bat`;
PowerShell `.venv\Scripts\Activate.ps1`; macOS/Linux `source .venv/bin/activate`.
If activation is blocked, use the environment interpreter directly:
`.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux.
Use Python 3.10 or newer. If your system calls the launcher python3 or py,
use that name consistently when creating the environment.

## Core edits

Only edit task_api/validation.py and task_api/tasks.py for the core exercise.

- TODO 1a: check and trim title. The Word tutorial gives a guided model.
- TODO 1b: check a supplied done value. False is valid.
- TODO 2: write the guided POST handler.
- TODO 3: complete three lines in the supplied PATCH handler.
- TODO 4: complete DELETE using the store result.

The body check, unknown-field loop, mode checks and final validation decision
are supplied. GET routes, Blueprint registration, storage, error handling,
the client and the main checker are supplied too. The main checker is read-only.
501 means an exercise placeholder is still present. It is not an installation error.

After the validator: `python check_validation.py` (10 small checks).
After POST: `python -m unittest verify_api -k create_location`.
After PATCH: `python -m unittest verify_api -k patch_keeps`.
After DELETE: `python -m unittest verify_api -k delete_empty_body`.
At the end: `python verify_api.py` (20 test methods with additional subcases).
These checkers construct their own applications; they do not need Terminal A.
api_client.py sends real HTTP requests and does need Terminal A.

## The same task throughout

Lina creates Prepare project proposal, completes it, sends a rejected mixed
update, then removes it. Keep each returned Location and use its actual ID.
After the last code edit, restart the server and record the entire sequence
without editing or restarting between requests. Restart/code reload resets this
teaching store to IDs 1, 2 and 3. It has no database.

The final submission includes notes.md, evidence.txt and checker_output.txt.
Do not submit .venv or __pycache__. The suggested core schedule is 120 minutes;
the Word tutorial separates optional comparisons and boundary/restart experiments.

## Comparisons

Use exercises/README.md for the Blueprint and PUT/PATCH observers. They are
independent applications. Run `python -m exercises.observe_blueprint` and
`python -m exercises.observe_put_patch` after the main workflow, or after class.
The main API continues to support PATCH and returns 405 for PUT.
