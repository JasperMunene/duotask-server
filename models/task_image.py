from . import db
from sqlalchemy_serializer import SerializerMixin

# ---------------------------------------------------------------------------
# Task Images
# ---------------------------------------------------------------------------
class TaskImage(db.Model, SerializerMixin):
    """TaskImage model for storing images associated with a task."""
    __tablename__ = 'task_images'

    serialize_rules = ('-task',)

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False, comment="Associated task id")
    image_url = db.Column(db.String(255), nullable=False, comment="URL to the task image")
    created_at = db.Column(db.DateTime, server_default=db.func.now())