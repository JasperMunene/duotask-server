from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Index


# ---------------------------------------------------------------------------
#  Profiles
# ---------------------------------------------------------------------------
class UserInfo(db.Model, SerializerMixin):
    """User info model for additional user details."""
    __tablename__ = 'user_info'
    __table_args__ = (
        Index('idx_user_info_user', 'user_id'),
    )

    serialize_rules = ('-user',)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(255), nullable=True, comment="User's short description")
    bio = db.Column(db.Text, nullable=True, comment="User's biography")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationship with User
    user = db.relationship("User", backref=db.backref("user_info", uselist=False, cascade="all, delete-orphan"))