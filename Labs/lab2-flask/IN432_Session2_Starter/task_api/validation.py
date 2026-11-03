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
        # TODO 1a: check the type first, then trim, then check the length.
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
        # TODO 1b: only a real JSON boolean is accepted (0, 1, "yes" are not).
        if type(value) is not bool:
            problems["done"] = "Done must be a JSON boolean"
        else:
            clean["done"] = value

    # Supplied: raise before returning any accepted fields if one field failed.
    if problems:
        raise ApiError(400, "validation_error", "Invalid task data", problems)
    return clean
