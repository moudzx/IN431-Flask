from flask import Blueprint, jsonify

bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


# TODO A: keep the public path /api/tasks without repeating its prefix.
@bp.get("/api/tasks")
def list_tasks():
    return jsonify([])
