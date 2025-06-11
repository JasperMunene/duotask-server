from . import db
from sqlalchemy_serializer import SerializerMixin

class PlatformWallet(db.Model, SerializerMixin):
    __tablename__ = 'platform_wallet'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(18, 2))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
