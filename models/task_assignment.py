from . import db
from sqlalchemy_serializer import SerializerMixin

# ---------------------------------------------------------------------------
#  Task Assignments
# ---------------------------------------------------------------------------
class TaskAssignment(db.Model, SerializerMixin):
    """TaskAssignment model recording which bid was accepted and the task assignment details."""
    __tablename__ = 'task_assignments'

    serialize_rules = (
        '-task',  # Don't serialize the parent task when serializing an assignment
        '-giver',  # Avoid serializing the full User object for the giver
        '-doer',  # Avoid serializing the full User object for the doer
        '-bid',  # Avoid serializing the related Bid object completely
    )

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    task_giver = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="User who posted the task")
    task_doer = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, comment="User assigned to perform the task")
    agreed_price = db.Column(db.Numeric(10, 2), nullable=False)
    bid_id = db.Column(db.Integer, db.ForeignKey('bids.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, comment="Assignment status: e.g., 'assigned', 'in_progress', 'completed', 'cancelled'")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    task = db.relationship("Task", backref=db.backref("assignments", cascade="all, delete-orphan", lazy=True))
    giver = db.relationship("User", foreign_keys=[task_giver], backref=db.backref("given_assignments", cascade="all, delete-orphan", lazy=True))
    doer = db.relationship("User", foreign_keys=[task_doer], backref=db.backref("assignments_received", cascade="all, delete-orphan", lazy=True))
    bid = db.relationship("Bid", backref=db.backref("assignment", uselist=False))
