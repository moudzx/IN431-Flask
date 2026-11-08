# Add CORS to the student's EXISTING Session 5 Flask app (do not replace backend)

The Session 5 app factory lives in `task_api/__init__.py`, inside `create_app`. Keep the same Flask routes, SQLAlchemy models, `instance/task_manager.db`, migrations, and commit logic.

1. In `task_api/__init__.py`, add `request` to the Flask import:

```python
from flask import Flask, jsonify, request
```

2. After `app.register_blueprint(bp)` inside `create_app`, insert:

```python
    allowed_frontends = {"http://127.0.0.1:5500", "http://localhost:5500"}

    @app.after_request
    def cors_for_independent_frontend(response):
        origin = request.headers.get("Origin")
        if request.path.startswith("/api/") and origin in allowed_frontends:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add("Vary", "Origin")
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PATCH, PUT, DELETE, OPTIONS"
            )
        return response
```

Flask automatically handles `OPTIONS` for conventional Flask routes (as used by this Session 5 app). These CORS response headers let the browser send JSON POST/PATCH and other cross-origin requests. They **do not** require putting frontend files into the Flask package and do not provide authentication.

3. Restart Flask and check from browser DevTools Network:
- GET `http://127.0.0.1:5000/api/tasks` returns 200 + `Access-Control-Allow-Origin` when the Origin header is `http://127.0.0.1:5500`.
- POST JSON triggers OPTIONS preflight; response includes permitted origin, methods, and `Content-Type` header.
- Origins not on the allow-list receive no CORS permission header.

Do NOT use unrestricted `*` origins in a credentialed deployment, and never make Flask's debug server publicly accessible.
