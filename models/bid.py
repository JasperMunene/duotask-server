from pygments.lexer import default

from . import db
from sqlalchemy_serializer import SerializerMixin

# ---------------------------------------------------------------------------
# Bids
# ---------------------------------------------------------------------------
class Bid(db.Model, SerializerMixin):
    """Bid model for offers made by users on tasks."""
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending', comment="Bid status: e.g., 'pending', 'accepted', 'rejected'")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    task = db.relationship("Task", backref=db.backref("bids", cascade="all, delete-orphan", lazy=True))
    user = db.relationship("User", backref=db.backref("bids", cascade="all, delete-orphan", lazy=True))