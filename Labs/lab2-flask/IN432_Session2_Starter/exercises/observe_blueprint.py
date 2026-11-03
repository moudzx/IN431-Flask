"""Compare route registration with separate in-process Flask applications."""
from flask import url_for
from werkzeug.routing import BuildError
from .blueprint_direct import create_app as direct_app
from .blueprint_grouped import create_app as grouped_app


def observe(label, factory, endpoint):
    app = factory()
    client = app.test_client()
    print("\n" + label)
    for path in ["/api/health", "/api/tasks", "/api/tasks/api/tasks"]:
        response = client.get(path)
        print("GET", path, "status", response.status_code,
              "body", response.get_json(silent=True))
    print("Registered API rules:")
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith("/api/"):
            print(" ", rule.rule, "endpoint", rule.endpoint)
    with app.test_request_context():
        try:
            print("url_for:", endpoint, "=>", url_for(endpoint))
        except BuildError:
            print("url_for:", endpoint, "=> no registered endpoint")


if __name__ == "__main__":
    observe("Direct registration", direct_app, "list_tasks")
    observe("Blueprint registration", grouped_app, "tasks.list_tasks")
