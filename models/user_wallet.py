# models/user_wallet.py

from . import db
from sqlalchemy_serializer import SerializerMixin

class Wallet(db.Model, SerializerMixin):
    __tablename__ = 'wallets'

    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(18, 2), default=0.00)
    currency = db.Column(db.String(10))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='wallets')
