"""Contract checks. Each test creates a fresh Flask app and store."""
import sys
import unittest
from task_api import create_app


class BaselineChecks(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True}).test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")
        self.assertIn("X-Request-ID", response.headers)

    def test_collection_and_item(self):
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 3)
        item = self.client.get("/api/tasks/1")
        self.assertEqual(item.json["title"], "Prepare lab")

    def test_missing_resource_and_route(self):
        for path in ("/api/tasks/999", "/api/tasks/abc", "/no-route"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertTrue(response.is_json)
                self.assertIn("error", response.json)

    def test_method_error_preserves_allow(self):
        response = self.client.put("/api/tasks/1", json={"title": "Example"})
        self.assertEqual(response.status_code, 405)
        self.assertTrue(response.is_json)
        self.assertIn("Allow", response.headers)
        self.assertIn("GET", response.headers["Allow"])


class WriteChecks(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def assert_error(self, response, status, code=None):
        self.assertEqual(response.status_code, status)
        self.assertTrue(response.is_json)
        self.assertIn("error", response.json)
        self.assertIn("message", response.json["error"])
        if code:
            self.assertEqual(response.json["error"]["code"], code)

    def test_create_location_and_default(self):
        response = self.client.post("/api/tasks", json={"title": "  New task  "})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["title"], "New task")
        self.assertIs(response.json["done"], False)
        self.assertEqual(response.headers["Location"], f'/api/tasks/{response.json["id"]}')
        self.assertEqual(self.client.get(response.headers["Location"]).json, response.json)

    def test_create_with_done(self):
        response = self.client.post("/api/tasks", json={"title": "New task", "done": True})
        self.assertEqual(response.status_code, 201)
        self.assertIs(response.json["done"], True)

    def test_unique_ids_and_repeated_post(self):
        first = self.client.post("/api/tasks", json={"title": "New task"})
        second = self.client.post("/api/tasks", json={"title": "New task"})
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(first.json["id"], second.json["id"])

    def test_rejected_create_leaves_collection_unchanged(self):
        invalid = [{}, [], None, "text", {"title": 42}, {"title": None},
                   {"title": "  "}, {"title": "ab"}, {"title": "x" * 121},
                   {"title": "Example", "done": "false"},
                   {"title": "Example", "done": 0},
                   {"title": "Example", "done": None},
                   {"title": "Example", "id": 99},
                   {"title": "Example", "extra": True}]
        import json
        before = self.client.get("/api/tasks").json
        for payload in invalid:
            with self.subTest(payload=payload):
                response = self.client.post("/api/tasks", data=json.dumps(payload),
                                            content_type="application/json")
                self.assert_error(response, 400, "validation_error")
                self.assertEqual(self.client.get("/api/tasks").json, before)

    def test_title_boundaries(self):
        for title in ("abc", "x" * 120):
            with self.subTest(length=len(title)):
                self.assertEqual(self.client.post("/api/tasks", json={"title": title}).status_code, 201)

    def test_bad_json_and_media_type(self):
        response = self.client.post("/api/tasks", data='{"title":', content_type="application/json")
        self.assert_error(response, 400, "bad_request")
        response = self.client.post("/api/tasks", data='{"title":"Example"}', content_type="text/plain")
        self.assert_error(response, 415, "unsupported_media_type")
        response = self.client.post("/api/tasks", data='{"title":"Example"}')
        self.assert_error(response, 415, "unsupported_media_type")

    def test_empty_json_body(self):
        response = self.client.post("/api/tasks", data="", content_type="application/json")
        self.assert_error(response, 400, "bad_request")

    def test_patch_keeps_omitted_fields(self):
        before = self.client.get("/api/tasks/1").json
        response = self.client.patch("/api/tasks/1", json={"done": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["title"], before["title"])
        self.assertEqual(response.json["id"], before["id"])
        self.assertIs(response.json["done"], True)

    def test_patch_normalisation_and_both_fields(self):
        response = self.client.patch("/api/tasks/1", json={"title": "  Updated title  ", "done": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["title"], "Updated title")
        self.assertIs(response.json["done"], True)

    def test_patch_invalid_fields_leave_all_data_unchanged(self):
        before = self.client.get("/api/tasks/1").json
        for payload in ({"title": "Should not be saved", "done": "yes"},
                        {}, {"title": 42}, {"done": 1}, {"id": 99},
                        {"extra": True}, {"title": "  "}):
            with self.subTest(payload=payload):
                response = self.client.patch("/api/tasks/1", json=payload)
                self.assert_error(response, 400, "validation_error")
                self.assertEqual(self.client.get("/api/tasks/1").json, before)

    def test_patch_false_is_a_valid_value(self):
        response = self.client.patch("/api/tasks/2", json={"done": False})
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.json["done"], False)

    def test_patch_retry_has_same_final_state(self):
        first = self.client.patch("/api/tasks/1", json={"done": True})
        second = self.client.patch("/api/tasks/1", json={"done": True})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json, second.json)

    def test_missing_patch_target(self):
        response = self.client.patch("/api/tasks/999", json={"done": True})
        self.assert_error(response, 404, "not_found")

    def test_delete_empty_body_then_missing(self):
        response = self.client.delete("/api/tasks/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        self.assertEqual(self.client.get("/api/tasks/1").status_code, 404)
        self.assert_error(self.client.delete("/api/tasks/1"), 404, "not_found")

    def test_deleted_ids_are_not_reused(self):
        created = self.client.post("/api/tasks", json={"title": "New task"})
        old_id = created.json["id"]
        self.client.delete(f"/api/tasks/{old_id}")
        new = self.client.post("/api/tasks", json={"title": "Another task"})
        self.assertGreater(new.json["id"], old_id)

    def test_new_app_has_fresh_store(self):
        self.client.post("/api/tasks", json={"title": "New task"})
        other = create_app({"TESTING": True}).test_client()
        self.assertEqual(len(other.get("/api/tasks").json), 3)


if __name__ == "__main__":
    if "--baseline" in sys.argv:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BaselineChecks)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
    unittest.main(verbosity=2)
