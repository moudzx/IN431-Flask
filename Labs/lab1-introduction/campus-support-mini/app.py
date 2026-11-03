from flask import Flask, jsonify, request

app = Flask(__name__)

TICKETS = [
    {"id": 1, "title": "Wi-Fi unavailable", "status": "OPEN"},
    {"id": 2, "title": "Printer offline", "status": "RESOLVED"},
    {"id": 3, "title": "Projector not detected", "status": "OPEN"},
]


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/tickets")
def list_tickets():
    status = request.args.get("status")
    if status is not None and status not in {"OPEN", "RESOLVED"}:
        return jsonify(error="Unsupported status"), 400
    items = TICKETS
    if status is not None:
        items = [t for t in TICKETS if t["status"] == status]
    return jsonify(items=items, count=len(items))

@app.get("/api/tickets/<int:id>")
def get_by_id(id):
    for t in TICKETS:
        if t["id"] == id:
            return jsonify(t), 200
    return jsonify(error="Not Found"), 404


if __name__ == "__main__":
    app.run()
