from . import db
from sqlalchemy_serializer import SerializerMixin

class TransactionLedger(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    sender_id = db.Column(db.Integer, nullable=True)  # None if system/platform
    receiver_id = db.Column(db.Integer, nullable=True)  # None if system/platform
    system = db.Column(db.Boolean, default=False, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    type = db.Column(db.String(50))  # e.g., 'peer_transfer', 'platform_fee', 'top_up'
    status = db.Column(db.String(20), default='pending')  # or 'completed', 'failed'
    balance = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    