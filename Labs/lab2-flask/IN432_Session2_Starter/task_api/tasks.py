from flask import Blueprint, current_app, jsonify, request, url_for
from .errors import ApiError
from .validation import validate_task

# The factory registers this group. Its prefix is part of every task URL.
bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def store():
    # Supplied helper: retrieve the TaskStore of the active Flask app.
    return current_app.extensions["task_store"]


@bp.get("")
def list_tasks():
    return jsonify(store().list())


@bp.get("/<int:task_id>")
def get_task(task_id):
    item = store().get(task_id)
    if item is None:
        raise ApiError(404, "not_found", "Task not found")
    return jsonify(item)


@bp.post("")
def create_task():
    # TODO 2: read JSON, validate, create, then return 201 with Location.
    payload = request.get_json()
    fields = validate_task(payload)
    item = store().create(fields)
    response = jsonify(item)
    response.status_code = 201
    response.headers["Location"] = url_for("tasks.get_task", task_id=item["id"])
    return response


@bp.patch("/<int:task_id>")
def update_task(task_id):
    # Supplied: find the target before reading its update.
    item = store().get(task_id)
    if item is None:
        raise ApiError(404, "not_found", "Task not found")
    payload = request.get_json()
    # TODO 3: validate in partial mode, update, respond.
    fields = validate_task(payload, partial=True)
    item = store().update(task_id, fields)
    return jsonify(item)


@bp.delete("/<int:task_id>")
def delete_task(task_id):
    # TODO 4: delete using the store result; 204 with an empty body on success.
    if not store().delete(task_id):
        raise ApiError(404, "not_found", "Task not found")
    return "", 204
