"""Isolated checks. Working SQLite files are never opened by this module."""
from pathlib import Path
import tempfile
import unittest
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch
from task_api import create_app
from task_api.extensions import db
from task_api.errors import ApiError
from task_api.models import Task
from task_api.store import TaskStore

class SetupChecks(unittest.TestCase):
    def test_import_and_stage(self):
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        response = app.test_client().get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["app"], "task_manager")

    def test_invalid_request_rejected_before_store(self):
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        self.assertEqual(app.test_client().post("/api/tasks", json={"title": "x"}).status_code, 400)

class ModelChecks(unittest.TestCase):
    def test_mapping(self):
        columns = Task.__table__.columns
        self.assertTrue({"id", "title", "done"}.issubset(columns.keys()), "Complete A1 first")
        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.title.nullable)
        self.assertEqual(columns.title.type.length, 120)
        self.assertFalse(columns.done.nullable)
        self.assertEqual(columns.done.type.__class__.__name__, "Boolean")
        self.assertIsNotNone(columns.done.default)
        self.assertIs(columns.done.default.arg, False)

class DatabaseCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.uri = "sqlite:///" + (Path(self.temp.name) / "checks.db").as_posix()
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": self.uri})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()
        self.temp.cleanup()

    def seed(self, title="Prepare proposal", done=False):
        task = Task(title=title, done=done)
        db.session.add(task)
        db.session.commit()
        return task

    def make_task(self, title="Prepare the API"):
        return self.seed(title)

    def make_project(self, name="Course Project"):
        project = Project(name=name)
        db.session.add(project)
        db.session.commit()
        return project

class RepresentationChecks(DatabaseCase):
    def test_public_fields(self):
        task = self.seed()
        self.assertEqual({key: task.to_dict()[key] for key in ("id", "title", "done")},
                         {"id": task.id, "title": "Prepare proposal", "done": False})

class CreateChecks(DatabaseCase):
    def test_create_and_read_persisted_task(self):
        response = self.client.post("/api/tasks", json={"title": "  Prepare proposal  "})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["title"], "Prepare proposal")
        self.assertFalse(response.json["done"])
        self.assertIn("Location", response.headers)
        db.session.remove()
        self.assertEqual(self.client.get(response.headers["Location"]).json, response.json)

    def test_invalid_create_adds_no_row(self):
        response = self.client.post("/api/tasks", json={"title": "x"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Task)).scalar(), 0)

    def test_read_missing(self):
        self.assertEqual(self.client.get("/api/tasks/999999").status_code, 404)

class ListChecks(DatabaseCase):
    def test_empty_and_populated_list(self):
        self.assertEqual(self.client.get("/api/tasks").json, [])
        a, b = self.seed(), self.seed("Second task")
        self.assertEqual([x["id"] for x in self.client.get("/api/tasks").json], [a.id, b.id])

class UpdateChecks(DatabaseCase):
    def test_false_and_omitted_title(self):
        task = self.seed(done=True)
        response = self.client.patch(f"/api/tasks/{task.id}", json={"done": False})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json["done"])
        self.assertEqual(response.json["title"], "Prepare proposal")
        db.session.remove()
        self.assertFalse(self.client.get(f"/api/tasks/{task.id}").json["done"])

    def test_invalid_mixed_payload_leaves_saved_title(self):
        task = self.seed()
        response = self.client.patch(f"/api/tasks/{task.id}", json={"title": "Rejected change", "done": "yes"})
        self.assertEqual(response.status_code, 400)
        db.session.refresh(task)
        self.assertEqual(task.title, "Prepare proposal")

    def test_missing_task(self):
        self.assertEqual(self.client.patch("/api/tasks/999999", json={"done": True}).status_code, 404)

class DeleteChecks(DatabaseCase):
    def test_delete_persists_and_response_empty(self):
        task = self.seed()
        url = f"/api/tasks/{task.id}"
        response = self.client.delete(url)
        self.assertEqual((response.status_code, response.data), (204, b""))
        db.session.remove()
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_missing_task(self):
        self.assertEqual(self.client.delete("/api/tasks/999999").status_code, 404)

class TransactionChecks(DatabaseCase):
    def test_flush_then_rollback(self):
        task = Task(title="Discard this draft", done=False)
        db.session.add(task)
        db.session.flush()
        self.assertIsInstance(task.id, int)
        db.session.rollback()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Task)).scalar(), 0)

    def test_supplied_commit_helper_recovers(self):
        task = Task(title="Failed write", done=False)
        db.session.add(task)
        with patch.object(db.session, "commit", side_effect=SQLAlchemyError("demonstration")):
            with self.assertRaises(ApiError):
                TaskStore()._commit()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Task)).scalar(), 0)
        self.seed("Valid after rollback")


from sqlalchemy.exc import IntegrityError
from task_api import models
from task_api.store import ProjectStore
from task_api.schema import upgrade_schema, MIGRATIONS
Project = getattr(models, "Project", None)
ProjectDetails = getattr(models, "ProjectDetails", None)
Tag = getattr(models, "Tag", None)
task_tags = getattr(models, "task_tags", None)


class ProjectChecks(DatabaseCase):
    def test_assign_move_and_unassign(self):
        task = self.make_task()
        first, second = self.make_project(), self.make_project("Another Project")
        url = "/api/tasks/" + str(task.id) + "/project"
        for expected in (first.id, second.id, None):
            response = self.client.put(url, json={"project_id": expected})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["project_id"], expected)
            self.assertEqual(db.session.get(Task, task.id).project_id, expected)

    def test_missing_project_preserves_assignment(self):
        task, project = self.make_task(), self.make_project()
        task.project = project
        db.session.commit()
        response = self.client.put("/api/tasks/" + str(task.id) + "/project",
                                   json={"project_id": 999999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(db.session.get(Task, task.id).project_id, project.id)

    def test_database_rejects_missing_parent(self):
        db.session.add(Task(title="Invalid parent", done=False, project_id=999999))
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Task)).scalar(), 0)


class DetailsChecks(DatabaseCase):
    def test_create_then_update_same_details(self):
        project = self.make_project()
        url = "/api/projects/" + str(project.id) + "/details"
        first = self.client.put(url, json={"description": "Initial description"})
        self.assertEqual(first.status_code, 201)
        second = self.client.put(url, json={"description": "Updated description"})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json["id"], first.json["id"])
        self.assertEqual(second.json["description"], "Updated description")

    def test_unique_foreign_key(self):
        project = self.make_project()
        db.session.add_all([ProjectDetails(project_id=project.id, description="One"),
                            ProjectDetails(project_id=project.id, description="Two")])
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(ProjectDetails)).scalar(), 0)


class TagChecks(DatabaseCase):
    def test_attach_repeatedly_and_share_tag(self):
        first, second = self.make_task(), self.make_task("Second task")
        tag = Tag(name="database")
        db.session.add(tag)
        db.session.commit()
        for task in (first, first, second):
            response = self.client.put(f"/api/tasks/{task.id}/tags/{tag.id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["tag_ids"], [tag.id])
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(task_tags)).scalar(), 2)

    def test_detach_keeps_other_link_and_entities(self):
        first, second = self.make_task(), self.make_task("Second task")
        tag = Tag(name="database")
        first.tags.append(tag)
        second.tags.append(tag)
        db.session.add(tag)
        db.session.commit()
        url = f"/api/tasks/{first.id}/tags/{tag.id}"
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertIsNotNone(db.session.get(Tag, tag.id))
        self.assertEqual(db.session.get(Task, first.id).tags, [])
        self.assertEqual([t.id for t in db.session.get(Task, second.id).tags], [tag.id])

    def test_duplicate_pair_rejected_by_database(self):
        task = self.make_task()
        tag = Tag(name="database")
        db.session.add(tag)
        db.session.commit()
        values = {"task_id": task.id, "tag_id": tag.id}
        db.session.execute(task_tags.insert().values(**values))
        db.session.commit()
        with self.assertRaises(IntegrityError):
            db.session.execute(task_tags.insert().values(**values))
        db.session.rollback()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(task_tags)).scalar(), 1)



class ReportChecks(DatabaseCase):
    def test_outer_join_keeps_unassigned_task(self):
        project = self.make_project()
        first, second = self.make_task(), self.make_task("Unassigned task")
        first.project = project
        db.session.commit()
        response = self.client.get("/api/reports/tasks-with-projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [
            {"id": first.id, "title": first.title, "project_name": project.name},
            {"id": second.id, "title": second.title, "project_name": None}])

    def test_count_includes_empty_project(self):
        first, empty = self.make_project(), self.make_project("Empty Project")
        task = self.make_task()
        task.project = first
        db.session.commit()
        response = self.client.get("/api/reports/project-counts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [
            {"id": first.id, "name": first.name, "task_count": 1},
            {"id": empty.id, "name": empty.name, "task_count": 0}])


class BundleChecks(DatabaseCase):
    def test_bundle_creates_related_rows(self):
        response = self.client.post("/api/project-bundles", json={
            "name": "Atomic Project", "description": "One transaction",
            "tasks": [{"title": "First task"}, {"title": "Second task"}]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json["task_ids"]), 2)
        self.assertEqual(response.json["details"]["project_id"], response.json["id"])

    def test_invalid_http_bundle_rejected_before_mutation(self):
        response = self.client.post("/api/project-bundles", json={
            "name": "Rejected Project", "description": "Invalid child",
            "tasks": [{"title": "Valid task"}, {"title": "x"}]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Project)).scalar(), 0)

    def test_database_failure_rolls_back_flushed_parent(self):
        # Deliberately bypass input validation to exercise the DB failure path.
        with self.assertRaises(ApiError) as caught:
            ProjectStore().create_bundle({"name": "Rollback Project", "description": "DB failure",
                "tasks": [{"title": "Valid task"}, {"title": "x"}]})
        self.assertEqual(caught.exception.status_code, 500)
        for model in (Project, ProjectDetails, Task):
            self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(model)).scalar(), 0)
        # The rolled-back scoped session can subsequently perform valid work.
        db.session.add(Project(name="Recovery Project"))
        db.session.commit()
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(Project)).scalar(), 1)

    def test_second_app_reads_same_committed_file(self):
        task, project = self.make_task(), self.make_project()
        task.project = project
        db.session.commit()
        task_id, project_id = task.id, project.id
        db.session.remove()
        second = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": self.uri})
        with second.app_context():
            response = second.test_client().get("/api/tasks/" + str(task_id))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["project_id"], project_id)
            db.session.remove()
            db.engine.dispose()

    def test_delete_project_keeps_tasks_and_shared_tags(self):
        task, project = self.make_task(), self.make_project()
        task.project = project
        project.details = ProjectDetails(description="Owned details")
        tag = Tag(name="database")
        task.tags.append(tag)
        db.session.add(tag)
        db.session.commit()
        task_id, project_id, tag_id = task.id, project.id, tag.id
        self.assertEqual(self.client.delete("/api/projects/" + str(project_id)).status_code, 204)
        db.session.expire_all()
        self.assertIsNone(db.session.get(Project, project_id))
        kept = db.session.get(Task, task_id)
        self.assertIsNotNone(kept)
        self.assertIsNone(kept.project_id)
        self.assertEqual([t.id for t in kept.tags], [tag_id])
        self.assertEqual(db.session.execute(db.select(db.func.count()).select_from(ProjectDetails)).scalar(), 0)

class ProjectModelChecks(DatabaseCase):
    def test_project_mapping_and_public_key(self):
        self.assertIsNotNone(Project, "Add Project in B1")
        relation = inspect(Task).relationships["project"]
        self.assertEqual(relation.back_populates, "tasks")
        self.assertFalse(relation.uselist)
        self.assertTrue(inspect(Project).relationships["tasks"].uselist)
        self.assertTrue(Task.__table__.columns.project_id.nullable)
        task = self.seed()
        self.assertIsNone(task.to_dict()["project_id"])

class DetailsModelChecks(DatabaseCase):
    def test_scalar_navigation_and_unique_foreign_key(self):
        self.assertIsNotNone(ProjectDetails, "Add ProjectDetails in C1")
        self.assertFalse(inspect(Project).relationships["details"].uselist)
        self.assertFalse(ProjectDetails.__table__.columns.project_id.nullable)
        self.assertTrue(ProjectDetails.__table__.columns.project_id.unique)

class TagModelChecks(DatabaseCase):
    def test_two_collections_and_composite_key(self):
        self.assertIsNotNone(Tag, "Add Tag in D1")
        self.assertEqual(set(task_tags.primary_key.columns.keys()), {"task_id","tag_id"})
        self.assertTrue(inspect(Task).relationships["tags"].uselist)
        self.assertTrue(inspect(Tag).relationships["tasks"].uselist)
        self.assertEqual(self.seed().to_dict()["tag_ids"], [])

class SchemaChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name)/"one_project.db"
        self.app = create_app({"TESTING": True,
                              "SQLALCHEMY_DATABASE_URI": "sqlite:///"+self.file.as_posix()})
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()
        self.temp.cleanup()

    def initial_task(self):
        upgrade_schema(1)
        with db.engine.begin() as c:
            c.exec_driver_sql("INSERT INTO tasks (title,done) VALUES (?,?)",
                             ("Keep my original task",1))

    def test_existing_task_survives_all_schema_versions(self):
        self.initial_task()
        for version in (2,3,4):
            result = upgrade_schema(version)
            self.assertTrue(Path(result["backup"]).is_file())
        task=db.session.get(Task,1)
        self.assertEqual(task.title,"Keep my original task")
        self.assertIs(task.done,True)
        self.assertIsNone(task.project_id)
        self.assertEqual(task.tags,[])
        with db.engine.connect() as c:
            self.assertEqual(c.exec_driver_sql("PRAGMA user_version").scalar(),4)
            self.assertEqual(c.exec_driver_sql("PRAGMA foreign_keys").scalar(),1)

    def test_repeat_is_noop_and_downgrade_refused(self):
        self.initial_task()
        upgrade_schema(4)
        self.assertFalse(upgrade_schema(4)["changed"])
        with self.assertRaises(ValueError):
            upgrade_schema(2)
        self.assertEqual(db.session.get(Task,1).title,"Keep my original task")

    def test_schema_failure_rolls_back_ddl_and_version(self):
        self.initial_task()
        original = MIGRATIONS[2]
        try:
            MIGRATIONS[2] = original + ["THIS IS NOT VALID SQL"]
            with self.assertRaises(Exception):
                upgrade_schema(2)
        finally:
            MIGRATIONS[2] = original
        with db.engine.connect() as c:
            self.assertEqual(c.exec_driver_sql("PRAGMA user_version").scalar(),1)
            self.assertIsNone(c.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE name='projects'").first())
            cols=[row[1] for row in c.exec_driver_sql("PRAGMA table_info(tasks)")]
            self.assertNotIn("project_id",cols)
            self.assertEqual(c.exec_driver_sql("SELECT title FROM tasks").scalar(),
                             "Keep my original task")


if __name__ == "__main__":
    unittest.main(verbosity=2)
