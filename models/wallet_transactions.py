from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

class WalletTransaction(db.Model, SerializerMixin):
    __tablename__ = 'wallet_transactions'

    ledgeidr_id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'), nullable=False)
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Numeric(18, 2))
    balance_after = db.Column(db.Numeric(18, 2))
    transaction_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(255))

    wallet = db.relationship('Wallet', backref='transactions')


# 🚫 Prevent updates to WalletTransaction rows
@event.listens_for(WalletTransaction, "before_update", propagate=True)
def prevent_wallet_txn_update(mapper, connection, target):
    raise IntegrityError(None, None, "WalletTransaction records are immutable and cannot be updated.")


# 🚫 Prevent deletes to WalletTransaction rows
@event.listens_for(WalletTransaction, "before_delete", propagate=True)
def prevent_wallet_txn_delete(mapper, connection, target):
    raise IntegrityError(None, None, "WalletTransaction records are immutable and cannot be deleted.")
