from flask import Blueprint, jsonify, request, url_for
from .errors import ApiError
from .store import TaskStore, ProjectStore, TagStore, ReportStore
from .validation import (validate_task, validate_name, validate_details,
                         validate_assignment, validate_bundle)

bp = Blueprint("api", __name__, url_prefix="/api")
tasks = TaskStore()
projects, tags, reports = ProjectStore(), TagStore(), ReportStore()

@bp.get("/tasks")
def task_list():
    return jsonify(tasks.list())

@bp.post("/tasks")
def task_create():
    data = tasks.create(validate_task(request.get_json()))
    return jsonify(data), 201, {"Location": url_for("api.task_get", task_id=data["id"])}

@bp.get("/tasks/<int:task_id>")
def task_get(task_id):
    data = tasks.get(task_id)
    if data is None:
        raise ApiError(404, "not_found", "Task not found")
    return jsonify(data)

@bp.patch("/tasks/<int:task_id>")
def task_update(task_id):
    data = tasks.update(task_id, validate_task(request.get_json(), partial=True))
    return jsonify(data)

@bp.delete("/tasks/<int:task_id>")
def task_delete(task_id):
    if not tasks.delete(task_id):
        raise ApiError(404, "not_found", "Task not found")
    return "", 204

@bp.put("/tasks/<int:task_id>/project")
def task_assign(task_id):
    return jsonify(tasks.assign(task_id, validate_assignment(request.get_json())))

@bp.put("/tasks/<int:task_id>/tags/<int:tag_id>")
def tag_attach(task_id, tag_id):
    return jsonify(tasks.attach_tag(task_id, tag_id))

@bp.delete("/tasks/<int:task_id>/tags/<int:tag_id>")
def tag_detach(task_id, tag_id):
    tasks.detach_tag(task_id, tag_id)
    return "", 204

@bp.get("/projects")
def project_list():
    return jsonify(projects.list())

@bp.post("/projects")
def project_create():
    result = projects.create(validate_name(request.get_json()))
    return jsonify(result), 201, {"Location": url_for("api.project_get", project_id=result["id"])}

@bp.get("/projects/<int:project_id>")
def project_get(project_id):
    return jsonify(projects.get(project_id))

@bp.delete("/projects/<int:project_id>")
def project_delete(project_id):
    projects.delete(project_id)
    return "", 204

@bp.put("/projects/<int:project_id>/details")
def details_put(project_id):
    result, created = projects.put_details(project_id, validate_details(request.get_json()))
    return jsonify(result), 201 if created else 200

@bp.post("/project-bundles")
def project_bundle():
    result = projects.create_bundle(validate_bundle(request.get_json()))
    return jsonify(result), 201, {"Location": url_for("api.project_get", project_id=result["id"])}

@bp.get("/tags")
def tag_list():
    return jsonify(tags.list())

@bp.post("/tags")
def tag_create():
    result = tags.create(validate_name(request.get_json(), maximum=40, minimum=2))
    return jsonify(result), 201

@bp.get("/reports/tasks-with-projects")
def task_report():
    return jsonify(reports.tasks_with_projects())

@bp.get("/reports/project-counts")
def count_report():
    return jsonify(reports.project_counts())
