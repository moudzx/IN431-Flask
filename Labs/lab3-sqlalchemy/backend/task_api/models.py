"""One evolving model module. Keep this file and the same database throughout."""
from .extensions import db

# BEGIN D1_TABLE
task_tags = db.Table(
    "task_tags",
    db.Column("task_id", db.Integer,
              db.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.Integer,
              db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
# END D1_TABLE

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    # BEGIN A1
    title = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    # END A1
    # BEGIN B1_TASK
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    project = db.relationship("Project", back_populates="tasks")
    # END B1_TASK
    # BEGIN D1_TASK
    tags = db.relationship(
        "Tag", secondary=task_tags, back_populates="tasks", order_by="Tag.id",
    )
    # END D1_TASK

    __table_args__ = (
        db.CheckConstraint("length(title) BETWEEN 3 AND 120", name="ck_task_title"),
        db.CheckConstraint("done IN (0, 1)", name="ck_task_done"),
        {"sqlite_autoincrement": True},
    )

    def to_dict(self):
        # BEGIN A2
        data = {"id": self.id, "title": self.title, "done": self.done}
        # END A2
        # BEGIN B1_PUBLIC
        data["project_id"] = self.project_id
        # END B1_PUBLIC
        # BEGIN D1_PUBLIC
        data["tag_ids"] = []
        for tag in self.tags:
            data["tag_ids"].append(tag.id)
        # END D1_PUBLIC

        return data

# BEGIN B1_PROJECT
class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship("Task", back_populates="project", order_by="Task.id")
    # BEGIN C1_PROJECT
    details = db.relationship(
        "ProjectDetails", back_populates="project", uselist=False,
        cascade="all, delete-orphan", single_parent=True,
    )
    # END C1_PROJECT

    __table_args__ = (
        db.CheckConstraint("length(name) BETWEEN 3 AND 100", name="ck_project_name"),
        {"sqlite_autoincrement": True},
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}
# END B1_PROJECT

# BEGIN C1_DETAILS
class ProjectDetails(db.Model):
    __tablename__ = "project_details"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    description = db.Column(db.String(500), nullable=False, default="")
    project = db.relationship("Project", back_populates="details")
    __table_args__ = (
        db.CheckConstraint("length(description) <= 500", name="ck_details_description"),
    )

    def to_dict(self):
        return {"id": self.id, "project_id": self.project_id,
                "description": self.description}
# END C1_DETAILS

# BEGIN D1_TAG
class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    tasks = db.relationship("Task", secondary=task_tags, back_populates="tags")
    __table_args__ = (
        db.CheckConstraint("length(name) BETWEEN 2 AND 40", name="ck_tag_name"),
        {"sqlite_autoincrement": True},
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}
# END D1_TAG
