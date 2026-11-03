"""A supplied, disposable demonstration. It does not open the lab database."""
from task_api import create_app
from task_api.extensions import db
from task_api.models import Task

if not {"title", "done"}.issubset(Task.__table__.columns.keys()):
    raise SystemExit("Complete A1 before running this demonstration.")
app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
with app.app_context():
    db.create_all()
    draft = Task(title="Disposable draft", done=False)
    print("After construction, id:", draft.id)
    db.session.add(draft)
    db.session.flush()
    print("After flush, id:", draft.id)
    db.session.rollback()
    print("Rows after rollback:", db.session.execute(
        db.select(db.func.count()).select_from(Task)).scalar_one())
    saved = Task(title="Committed example", done=False)
    db.session.add(saved)
    db.session.commit()
    print("Rows after commit:", db.session.execute(
        db.select(db.func.count()).select_from(Task)).scalar_one())
    print("This in-memory demonstration ends here; it did not change your working task_manager.db.")
