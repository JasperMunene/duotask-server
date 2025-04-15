from . import db
from sqlalchemy_serializer import SerializerMixin


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    __table_args__ = (
        db.Index('ix_reviews_reviewee_id', 'reviewee_id'),
    )

    id = db.Column(db.Integer, primary_key=True)

    task_assignment_id = db.Column(
        db.Integer,
        db.ForeignKey('task_assignments.id', ondelete='CASCADE'),
        nullable=False
    )

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False  # User giving the review
    )

    reviewee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False  # User receiving the review
    )

    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    assignment = db.relationship(
        "TaskAssignment",
        backref=db.backref("review", uselist=False, passive_deletes=True)
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_id],
        backref=db.backref("reviews_given", cascade="all, delete-orphan", passive_deletes=True, lazy=True)
    )

    reviewee = db.relationship(
        "User",
        foreign_keys=[reviewee_id],
        backref=db.backref("reviews_received", cascade="all, delete-orphan", passive_deletes=True, lazy=True)
    )
