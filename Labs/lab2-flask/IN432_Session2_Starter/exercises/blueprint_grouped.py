from flask import Flask, jsonify
from .blueprint_routes import bp


def create_app():
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    # TODO B: register the imported blueprint on app here.
    return app
