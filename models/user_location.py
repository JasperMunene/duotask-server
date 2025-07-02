from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Index

# ---------------------------------------------------------------------------
#  User Location Model
# ---------------------------------------------------------------------------
class UserLocation(db.Model, SerializerMixin):
    """Stores user's geographical location and address details."""
    __tablename__ = 'user_location'
    __table_args__ = (
        Index('idx_user_location_user', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    latitude = db.Column(db.Float, nullable=True)   # e.g. -1.2921
    longitude = db.Column(db.Float, nullable=True)  # e.g. 36.8219
    street = db.Column(db.String(120), nullable=True)  # e.g. "Koinange St"
    area = db.Column(db.String(120), nullable=True)    # e.g. "CBD"
    state = db.Column(db.String(120), nullable=True)   # e.g. "Nairobi County"
    country = db.Column(db.String(120), nullable=True) # e.g. "Kenya"

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Exclude user relationship from serialization
    serialize_rules = ('-user',)

    # Optional: define relationship if needed
    user = db.relationship('User', backref=db.backref('locations', lazy=True))
