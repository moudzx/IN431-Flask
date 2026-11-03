from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/tasks")
    def list_tasks():
        return jsonify([])

    return app
