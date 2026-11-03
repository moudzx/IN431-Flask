# Guided comparisons for Session 2

These exercises complement the classroom prediction slides. Use a Python
environment with the project's requirements installed. Open the terminal in
the folder containing requirements.txt. Both observation scripts use Flask's
in-process test client and require no running server.

## Exercise A: direct routes and Blueprint routes

The minimal comparison has an empty task list. It is a separate application
from the core lab's seeded TaskStore.

1. Read blueprint_direct.py, blueprint_routes.py and blueprint_grouped.py.
2. Predict the status for GET /api/tasks in each version.
3. Run `python -m exercises.observe_blueprint`.
4. Complete TODO B by registering bp before the factory returns app.
5. Run the observer again and locate the duplicated /api/tasks/api/tasks path.
6. Complete TODO A by using an empty local path in the blueprint decorator.
7. Run again. Both versions should expose GET /api/tasks and return 200 with [].

Record why the blueprint needs registration, which URL prefix applies, and why
url_for uses list_tasks in one version and tasks.list_tasks in the other.
Keep /api/health as a direct app route. Keep the core task_api files separate.

## Exercise B: PUT replacement and PATCH changes

The supplied put_patch_demo.py is a complete, independent comparison API with
the path /demo/tasks/4. Its original task is:

```json
{"id":4,"title":"Prepare project proposal","done":false}
```

For this comparison contract, PUT requires title and done, rejects supplied id,
and replaces the writable state. PATCH accepts a nonempty object of supplied
fields and keeps omitted fields. Both validate all fields before mutation.
Each case starts from a fresh task, not from the previous case's result.

Predict the status and entire task after each request before running:

- A: PATCH {"done":true}
- B: PUT {"done":true}
- C: PUT {"title":"Revised project proposal","done":true}
- D: PATCH {"title":"Revised project proposal"}

Run `python -m exercises.observe_put_patch` and compare your predictions with
the output. Explain why B is rejected rather than deleting or guessing a title.
The rule for omitted PUT fields belongs to this documented comparison contract.
Explain the retry output: this replacement and this field-setting PATCH each
produce the same final representation on a repeated request. PATCH as a method
is not generally idempotent.

The main task_api implements PATCH and returns 405 for PUT. These comparison
files do not add PUT to its routes and do not change verify_api.py.

The class can discuss predictions during the guided lesson. Laptop extensions
take about 15 to 20 minutes and can follow the 120-minute core tutorial or be
completed after class. Keep their observations separate from Lina's main evidence.
