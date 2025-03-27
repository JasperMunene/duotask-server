from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData, Index

# Configure naming convention for database constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    """User model representing application users."""
    __tablename__ = 'users'

    # Serialization rules to exclude sensitive information
    serialize_rules = ('-password', '-verification_token', '-reset_token', '-reset_expires_at')

    id = db.Column(db.UUID, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(15), comment="Stored in E.164 format")
    image = db.Column(db.String(255), nullable=True, comment="URL to profile image")
    verification_token = db.Column(db.String(6), nullable=True)
    verification_expires_at = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    reset_token = db.Column(db.String(64), nullable=True)
    reset_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),
                          server_onupdate=db.func.now())


Index('idx_verification', User.verification_token, User.verification_expires_at)

class UserInfo(db.Model, SerializerMixin):
    """User info model for additional user details."""
    __tablename__ = 'user_info'

    # Serialization rules to exclude sensitive information
    serialize_rules = ('-user',)

    id = db.Column(db.UUID, primary_key=True)
    user_id = db.Column(db.UUID, db.ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(255), nullable=True, comment="User's short description")
    bio = db.Column(db.Text, nullable=True, comment="User's biography")
    rating = db.Column(db.Float, default=0.0, nullable=False, comment="User's rating (0.0 - 5.0)")
    completion_rate = db.Column(db.Float, default=0.0, nullable=False, comment="Task completion rate (0-100%)")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Define relationship
    user = db.relationship("User", backref=db.backref("user_info", uselist=False, cascade="all, delete-orphan"))


# Indexes for performance optimization
Index('idx_user_info_user', UserInfo.user_id)
Index('idx_user_info_rating', UserInfo.rating)
Index('idx_user_info_completion', UserInfo.completion_rate)
