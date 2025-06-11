from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

class FloatWalletLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    direction = db.Column(db.String(10))  # 'in' or 'out'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    source = db.Column(db.String(100))  # 'bank', 'mpesa', 'user', 'business_payout'
    destination = db.Column(db.String(100))  # 'float', 'user', 'bank', etc
    purpose = db.Column(db.String(100))  # 'float_topup', 'payout', 'revenue_transfer'
    status = db.Column(db.String(20), default='pending')
    balance = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# 🚫 Prevent updates to float rows
@event.listens_for(FloatWalletLedger, "before_update", propagate=True)
def prevent_wallet_txn_update(mapper, connection, target):
    raise IntegrityError(None, None, "Float records are immutable and cannot be updated.")


# 🚫 Prevent deletes to float rows
@event.listens_for(FloatWalletLedger, "before_delete", propagate=True)
def prevent_wallet_txn_delete(mapper, connection, target):
    raise IntegrityError(None, None, "Float records are immutable and cannot be deleted.")
