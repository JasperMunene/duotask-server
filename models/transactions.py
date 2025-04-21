from . import db
from sqlalchemy_serializer import SerializerMixin

class Transaction(db.Model, SerializerMixin):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    from_wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'), nullable=False)
    to_wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'), nullable=False)
    amount = db.Column(db.Numeric(18, 2))
    transaction_fee = db.Column(db.Numeric(18, 2))
    transaction_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    type = db.Column(db.String(50))
    eference = db.Column(db.String(255))
    from_wallet = db.relationship('Wallet', foreign_keys=[from_wallet_id], backref='sent_transactions')
    to_wallet = db.relationship('Wallet', foreign_keys=[to_wallet_id], backref='received_transactions')
