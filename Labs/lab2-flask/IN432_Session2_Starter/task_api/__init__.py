from uuid import uuid4
from flask import Flask, g, jsonify
from .errors import register_error_handlers
from .store import TaskStore
from .tasks import bp


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)
    app.extensions["task_store"] = TaskStore()
    register_error_handlers(app)
    app.register_blueprint(bp)

    @app.before_request
    def identify_request():
        g.request_id = uuid4().hex

    @app.after_request
    def add_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="advanced-web-api")

    return app
