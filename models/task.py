from . import db
from sqlalchemy_serializer import SerializerMixin

# Association table for the many-to-many relationship between tasks and categories
task_categories = db.Table(
    'task_categories',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete="CASCADE"), primary_key=True)
)

# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
class Task(db.Model, SerializerMixin):
    """Task model representing a task posted on the platform."""
    __tablename__ = 'tasks'

    serialize_rules = ('-user.tasks', '-location.tasks', '-categories.tasks', '-images.task')

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="Task creator")
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    work_mode = db.Column(db.String(20), nullable=False, comment="Either 'remote' or 'physical'")
    location_id = db.Column(db.Integer, db.ForeignKey('task_locations.id', ondelete="SET NULL"), nullable=True, comment="Required if work_mode is physical")
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False, comment="Scheduling type: 'specific_day', 'before_day', or 'flexible'")
    specific_date = db.Column(db.DateTime, nullable=True, comment="Exact date if schedule_type is 'specific_day'")
    deadline_date = db.Column(db.DateTime, nullable=True, comment="Deadline date if schedule_type is 'before_day'")
    preferred_time = db.Column(db.Time, nullable=True, comment="Preferred time if schedule_type is 'flexible'")
    status = db.Column(db.String(20), nullable=False, comment="Task status: e.g., 'open', 'in_progress', 'completed', 'cancelled'", server_default="open")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    user = db.relationship("User", backref=db.backref("tasks", cascade="all, delete-orphan", lazy=True))
    location = db.relationship("TaskLocation", backref=db.backref("tasks", cascade="all, delete-orphan", lazy=True))
    categories = db.relationship('Category', secondary=task_categories, backref='tasks')
    images = db.relationship("TaskImage", backref=db.backref("task", lazy=True), cascade="all, delete-orphan", single_parent=True)

