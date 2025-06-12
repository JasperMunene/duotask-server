from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

class WalletTransaction(db.Model, SerializerMixin):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50)) # e.g., 'credit', 'debit'
    amount = db.Column(db.Numeric(18, 2))
    transaction_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(255))
    transaction_fees = db.Column(db.Numeric(18, 2), default=0.00)
    status = db.Column(db.String(20), default='pending')  # e.g., 'pending', 'completed', 'failed'


# 🚫 Prevent updates to WalletTransaction rows
@event.listens_for(WalletTransaction, "before_update", propagate=True)
def prevent_wallet_txn_update(mapper, connection, target):
    raise IntegrityError(None, None, "WalletTransaction records are immutable and cannot be updated.")


# 🚫 Prevent deletes to WalletTransaction rows
@event.listens_for(WalletTransaction, "before_delete", propagate=True)
def prevent_wallet_txn_delete(mapper, connection, target):
    raise IntegrityError(None, None, "WalletTransaction records are immutable and cannot be deleted.")