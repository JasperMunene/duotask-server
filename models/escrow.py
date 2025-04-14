from . import db
from sqlalchemy_serializer import SerializerMixin

class Escrow(db.Model, SerializerMixin):
    __tablename__ = 'escrow'

    escrow_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.transaction_id'), nullable=False)
    wallet_id_from = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'), nullable=False)
    wallet_id_to = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'), nullable=False)
    amount = db.Column(db.Numeric(18, 2))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    release_date = db.Column(db.DateTime)
    refund_date = db.Column(db.DateTime)

    transaction = db.relationship('Transaction', backref='escrow')
    wallet_from = db.relationship('Wallet', foreign_keys=[wallet_id_from])
    wallet_to = db.relationship('Wallet', foreign_keys=[wallet_id_to])
