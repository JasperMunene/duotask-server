from . import db
from sqlalchemy_serializer import SerializerMixin

class FloatWalletLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    direction = db.Column(db.String(10))  # 'in' or 'out'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    source = db.Column(db.String(100))  # 'bank', 'mpesa', 'user', 'business_payout'
    destination = db.Column(db.String(100))  # 'float', 'user', 'bank', etc
    purpose = db.Column(db.String(100))  # 'float_topup', 'payout', 'revenue_transfer'
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
