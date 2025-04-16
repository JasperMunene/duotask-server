from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Index
from utils.encryption import encrypt_data, decrypt_data

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
    mpesa_number = db.Column("mpesa_number", db.String(255), nullable=True)
    # Relationship with User
    user = db.relationship("User", backref=db.backref("user_info", uselist=False, cascade="all, delete-orphan"))
    
    
    # encrypt mpesa_number
    @property
    def mpesa_number(self):
        return decrypt_data(self.mpesa_number) if self.mpesa_number else None

    @mpesa_number.setter
    def mpesa_number(self, value):
        self.mpesa_number = encrypt_data(value)