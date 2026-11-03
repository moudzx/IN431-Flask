"""Independent comparison API: PUT replaces writable state, PATCH sets fields.

This teaching contract requires title and done on PUT. The core task API is
unchanged and still rejects PUT with 405.
"""
from flask import Flask, jsonify, request

INITIAL_TASK = {"id": 4, "title": "Prepare project proposal", "done": False}


class InvalidFields(Exception):
    def __init__(self, fields):
        self.fields = fields


def validate_fields(payload, replacement=False):
    if not isinstance(payload, dict):
        raise InvalidFields({"body": "Send a JSON object"})
    problems, clean = {}, {}
    for key in payload.keys() - {"title", "done"}:
        problems[key] = "Read-only field" if key == "id" else "Unknown field"
    if replacement:
        for key in ("title", "done"):
            if key not in payload:
                problems[key] = "Required for this PUT replacement"
    elif not payload:
        problems["body"] = "Supply at least one writable field"
    if "title" in payload:
        value = payload["title"]
        if not isinstance(value, str):
            problems["title"] = "Title must be a string"
        else:
            value = value.strip()
            if not 3 <= len(value) <= 120:
                problems["title"] = "Use 3 to 120 characters after trimming"
            else:
                clean["title"] = value
    if "done" in payload:
        if type(payload["done"]) is not bool:
            problems["done"] = "Done must be a JSON boolean"
        else:
            clean["done"] = payload["done"]
    if problems:
        raise InvalidFields(problems)
    return clean


def create_app():
    app = Flask(__name__)
    app.extensions["demo_task"] = INITIAL_TASK.copy()

    @app.errorhandler(InvalidFields)
    def invalid_fields(error):
        return jsonify(error={"code": "validation_error", "fields": error.fields}), 400

    @app.get("/demo/tasks/4")
    def get_task():
        return jsonify(app.extensions["demo_task"])

    @app.put("/demo/tasks/4")
    def replace_task():
        fields = validate_fields(request.get_json(), replacement=True)
        app.extensions["demo_task"] = {"id": 4, **fields}
        return jsonify(app.extensions["demo_task"])

    @app.patch("/demo/tasks/4")
    def update_task():
        fields = validate_fields(request.get_json())
        updated = app.extensions["demo_task"].copy()
        updated.update(fields)
        app.extensions["demo_task"] = updated
        return jsonify(updated)

    return app
