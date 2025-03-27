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

    # Define an index on otp_code and otp_expires_at via __table_args__
    __table_args__ = (
        Index('idx_verification', 'otp_code', 'otp_expires_at'),
    )

    # Serialization rules to exclude sensitive information
    serialize_rules = ('-password', '-otp_code', '-reset_token', '-reset_expires_at')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(15), comment="Stored in E.164 format")
    image = db.Column(db.String(255), nullable=True, comment="URL to profile image")
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    reset_token = db.Column(db.String(64), nullable=True)
    reset_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
