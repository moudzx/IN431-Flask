"""Functional smoke checks for CRUD, CORS and SQLite persistence.

Run: python -m unittest smoke_test -v
Creates a temporary database only; never touches your coursework data.
"""
import tempfile
import unittest
from pathlib import Path
from task_api import create_app
from task_api.schema import upgrade_schema
from task_api.extensions import db

class IndependentFrontendBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.uri = "sqlite:///" + (Path(self.temp.name) / "test.db").as_posix()
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": self.uri})
        with self.app.app_context():
            upgrade_schema(4)
        self.client = self.app.test_client()
        self.origin = {"Origin": "http://127.0.0.1:5500"}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        self.temp.cleanup()

    def test_crud_and_json(self):
        self.assertEqual(self.client.get("/api/tasks").json, [])
        created = self.client.post("/api/tasks", json={"title": "Prepare the demo"}, headers=self.origin)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.headers.get("Access-Control-Allow-Origin"), self.origin["Origin"])
        id = created.json["id"]
        read = self.client.get(f"/api/tasks/{id}")
        self.assertEqual(read.json["title"], "Prepare the demo")
        changed = self.client.patch(f"/api/tasks/{id}", json={"done": True})
        self.assertEqual(changed.status_code, 200)
        self.assertTrue(changed.json["done"])
        self.assertEqual(self.client.delete(f"/api/tasks/{id}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/tasks/{id}").status_code, 404)

    def test_cors_preflight(self):
        result = self.client.options('/api/tasks', headers={
            **self.origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers.get('Access-Control-Allow-Origin'), self.origin['Origin'])
        self.assertIn('POST', result.headers.get('Access-Control-Allow-Methods', ''))

    def test_restart_keeps_saved_task(self):
        created = self.client.post("/api/tasks", json={"title": "Keep this task"})
        id = created.json["id"]
        # Simulate a second Flask app instance pointing to the same SQLite file.
        second = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": self.uri})
        read = second.test_client().get(f"/api/tasks/{id}")
        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.json["title"], "Keep this task")
        with second.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_session5_projects_and_tags_remain(self):
        project = self.client.post("/api/projects", json={"name": "Web Development"})
        tag = self.client.post("/api/tags", json={"name": "API"})
        self.assertEqual((project.status_code, tag.status_code), (201, 201))
        task = self.client.post("/api/tasks", json={"title": "Connect frontend"})
        tid = task.json['id']
        project_id, tag_id = project.json['id'], tag.json['id']
        assign = self.client.put(f"/api/tasks/{tid}/project", json={"project_id": project_id})
        attach = self.client.put(f"/api/tasks/{tid}/tags/{tag_id}")
        self.assertEqual((assign.status_code, attach.status_code), (200, 200))
        self.assertEqual(attach.json["project_id"], project_id)
        self.assertIn(tag_id, attach.json["tag_ids"])

if __name__ == '__main__':
    unittest.main()
