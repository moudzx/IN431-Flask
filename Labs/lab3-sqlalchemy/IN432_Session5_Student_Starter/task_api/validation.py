from .errors import ApiError


def validate_task(payload, partial=False):
    """Check the data without changing stored tasks.

    partial=False: a new task needs a title.
    partial=True: check only supplied fields, but reject an empty update.
    """
    # Supplied: the body must be a Python dictionary.
    if not isinstance(payload, dict):
        raise ApiError(400, "validation_error", "Invalid task data",
                       {"body": "Send a JSON object"})

    # Supplied: two separate dictionaries collect results and feedback.
    clean = {}
    problems = {}

    # Supplied: iterating over a dictionary visits its keys.
    allowed_fields = ["title", "done"]
    for key in payload:
        if key not in allowed_fields:
            if key == "id":
                problems[key] = "Read-only field"
            else:
                problems[key] = "Unknown field"

    # Supplied: POST requires title; PATCH requires at least one field.
    if partial and not payload:
        problems["body"] = "Supply at least one writable field"
    if not partial and "title" not in payload:
        problems["title"] = "Title is required"

    if "title" in payload:
        value = payload["title"]
        if not isinstance(value, str):
            problems["title"] = "Title must be a string"
        else:
            value = value.strip()
            if len(value) < 3 or len(value) > 120:
                problems["title"] = "Use 3 to 120 characters after trimming"
            else:
                clean["title"] = value

    if "done" in payload:
        value = payload["done"]
        if type(value) is not bool:
            problems["done"] = "Done must be a JSON boolean"
        else:
            clean["done"] = value

    # Supplied: raise before returning any accepted fields if one field failed.
    if problems:
        raise ApiError(400, "validation_error", "Invalid task data", problems)
    return clean


def object_fields(payload, allowed, required):
    if not isinstance(payload, dict):
        raise ApiError(400, "validation_error", "Send a JSON object")
    if set(payload) - set(allowed) or set(required) - set(payload):
        raise ApiError(400, "validation_error", "Check required and allowed fields")

def text_value(value, minimum, maximum):
    if not isinstance(value, str):
        raise ApiError(400, "validation_error", "Text value required")
    value = value.strip()
    if not minimum <= len(value) <= maximum:
        raise ApiError(400, "validation_error", "Text length is outside the allowed range")
    return value

def validate_name(payload, maximum=100, minimum=3):
    object_fields(payload, ["name"], ["name"])
    return {"name": text_value(payload["name"], minimum, maximum)}

def validate_details(payload):
    object_fields(payload, ["description"], ["description"])
    return {"description": text_value(payload["description"], 0, 500)}

def validate_assignment(payload):
    object_fields(payload, ["project_id"], ["project_id"])
    value = payload["project_id"]
    if value is not None and (type(value) is not int or value < 1):
        raise ApiError(400, "validation_error", "project_id must be a positive integer or null")
    return value

def validate_bundle(payload):
    object_fields(payload, ["name", "description", "tasks"], ["name", "description", "tasks"])
    name = text_value(payload["name"], 3, 100)
    description = text_value(payload["description"], 0, 500)
    if not isinstance(payload["tasks"], list) or not 1 <= len(payload["tasks"]) <= 10:
        raise ApiError(400, "validation_error", "Supply 1 to 10 tasks")
    # Validate EVERY child before calling the persistence layer.
    tasks = [validate_task(task) for task in payload["tasks"]]
    return {"name": name, "description": description, "tasks": tasks}
