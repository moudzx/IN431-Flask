from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from .extensions import db
from .errors import ApiError
from .models import Task

def require(model, object_id):
    obj = db.session.get(model, object_id)
    if obj is None:
        raise ApiError(404, "not_found", model.__name__ + " not found")
    return obj

def related_model(name):
    # Supplied: make later routes return 501 until that model has been added.
    from . import models
    model = getattr(models, name, None)
    if model is None:
        raise ApiError(501, "unfinished_model", "Add the " + name + " mapping first")
    return model

class BaseStore:
    def _commit(self):
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise ApiError(500, "database_error", "Database operation failed")

class TaskStore(BaseStore):
    def get(self, task_id):
        task = db.session.get(Task, task_id)
        return None if task is None else task.to_dict()

    def create(self, fields):
        # BEGIN A3
        task = Task(title=fields["title"], done=fields.get("done", False))
        db.session.add(task)
        self._commit()
        return task.to_dict()
        # END A3

    def list(self):
        # BEGIN A4
        statement = db.select(Task).order_by(Task.id)
        tasks = db.session.execute(statement).scalars().all()
        result = []
        for task in tasks:
            result.append(task.to_dict())
        return result
        # END A4

    def update(self, task_id, fields):
        # BEGIN A5
        task = db.session.get(Task, task_id)
        if task is None:
            raise ApiError(404, "not_found", "Task not found")
        if "title" in fields:
            task.title = fields["title"]
        if "done" in fields:
            task.done = fields["done"]
        self._commit()
        return task.to_dict()
        # END A5

    def delete(self, task_id):
        # BEGIN A6
        task = db.session.get(Task, task_id)
        if task is None:
            return False
        db.session.delete(task)
        self._commit()
        return True
        # END A6

    def assign(self, task_id, project_id):
        Project = related_model("Project")
        # BEGIN B2
        task = require(Task, task_id)
        project = None
        if project_id is not None:
            project = require(Project, project_id)
        task.project = project
        self._commit()
        return task.to_dict()
        # END B2

    def attach_tag(self, task_id, tag_id):
        Tag = related_model("Tag")
        # BEGIN D2
        task = require(Task, task_id)
        tag = require(Tag, tag_id)
        if tag not in task.tags:
            task.tags.append(tag)
        self._commit()
        return task.to_dict()
        # END D2

    def detach_tag(self, task_id, tag_id):
        Tag = related_model("Tag")
        # BEGIN D3
        task = require(Task, task_id)
        tag = require(Tag, tag_id)
        if tag in task.tags:
            task.tags.remove(tag)
        self._commit()
        # END D3

class ProjectStore(BaseStore):
    def create(self, fields):
        Project = related_model("Project")
        project = Project(name=fields["name"])
        db.session.add(project)
        self._commit()
        return project.to_dict()

    def list(self):
        Project = related_model("Project")
        rows = db.session.execute(db.select(Project).order_by(Project.id)).scalars().all()
        return [p.to_dict() for p in rows]

    def get(self, project_id):
        Project = related_model("Project")
        project = require(Project, project_id)
        data = project.to_dict()
        data["task_ids"] = [task.id for task in project.tasks]
        # Details is introduced only in part C.
        details = getattr(project, "details", None)
        data["details"] = None if details is None else details.to_dict()
        return data

    def put_details(self, project_id, fields):
        Project = related_model("Project")
        ProjectDetails = related_model("ProjectDetails")
        # BEGIN C2
        project = require(Project, project_id)
        created = project.details is None
        if created:
            project.details = ProjectDetails(description=fields["description"])
        else:
            project.details.description = fields["description"]
        self._commit()
        return project.details.to_dict(), created
        # END C2

    def create_bundle(self, fields):
        Project = related_model("Project")
        ProjectDetails = related_model("ProjectDetails")
        # BEGIN E3
        try:
            project = Project(name=fields["name"])
            db.session.add(project)
            db.session.flush()
            project.details = ProjectDetails(description=fields["description"])
            for item in fields["tasks"]:
                task = Task(title=item["title"], done=item.get("done", False))
                task.project = project
                db.session.add(task)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise ApiError(500, "database_error", "Database operation failed")
        return self.get(project.id)
        # END E3

    def delete(self, project_id):
        Project = related_model("Project")
        project = require(Project, project_id)
        for task in list(project.tasks):
            task.project = None
        db.session.delete(project)
        self._commit()

class TagStore(BaseStore):
    def list(self):
        Tag = related_model("Tag")
        rows = db.session.execute(db.select(Tag).order_by(Tag.id)).scalars().all()
        return [tag.to_dict() for tag in rows]

    def create(self, fields):
        Tag = related_model("Tag")
        if db.session.execute(db.select(Tag).where(Tag.name == fields["name"])).scalar_one_or_none():
            raise ApiError(409, "conflict", "A tag with this name already exists")
        tag = Tag(name=fields["name"])
        db.session.add(tag)
        self._commit()
        return tag.to_dict()

class ReportStore:
    def tasks_with_projects(self):
        Project = related_model("Project")
        # BEGIN E1
        statement = (
            db.select(Task.id, Task.title, Project.name.label("project_name"))
            .select_from(Task).outerjoin(Task.project).order_by(Task.id)
        )
        rows = db.session.execute(statement).all()
        return [{"id": row.id, "title": row.title,
                 "project_name": row.project_name} for row in rows]
        # END E1

    def project_counts(self):
        Project = related_model("Project")
        # BEGIN E2
        statement = (
            db.select(Project.id, Project.name, func.count(Task.id).label("task_count"))
            .outerjoin(Project.tasks)
            .group_by(Project.id, Project.name).order_by(Project.id)
        )
        rows = db.session.execute(statement).all()
        return [{"id": row.id, "name": row.name,
                 "task_count": row.task_count} for row in rows]
        # END E2
