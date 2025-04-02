from . import db
from sqlalchemy_serializer import SerializerMixin


# ---------------------------------------------------------------------------
#  Task Locations
# ---------------------------------------------------------------------------
class TaskLocation(db.Model, SerializerMixin):
    """TaskLocation model storing physical location details for tasks."""
    __tablename__ = 'task_locations'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(9, 6), nullable=False, comment="Latitude coordinate")
    longitude = db.Column(db.Numeric(9, 6), nullable=False, comment="Longitude coordinate")
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=True, comment="Optional area or neighborhood")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())