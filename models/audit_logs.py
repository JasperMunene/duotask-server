from . import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

class AuditLog(db.Model, SerializerMixin):
    __tablename__ = 'audit_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.transaction_id'))
    escrow_id = db.Column(db.Integer, db.ForeignKey('escrow.escrow_id'))
    event = db.Column(db.Text)
    event_date = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))

    user = db.relationship('User', backref='audit_logs')
    wallet = db.relationship('Wallet', backref='audit_logs')
    transaction = db.relationship('Transaction', backref='audit_logs')
    escrow = db.relationship('Escrow', backref='audit_logs')


# 🚫 Prevent updates to AuditLog rows
@event.listens_for(AuditLog, "before_update", propagate=True)
def prevent_update(mapper, connection, target):
    raise IntegrityError(None, None, "AuditLog records are immutable and cannot be updated.")


# 🚫 Prevent deletes to AuditLog rows
@event.listens_for(AuditLog, "before_delete", propagate=True)
def prevent_delete(mapper, connection, target):
    raise IntegrityError(None, None, "AuditLog records are immutable and cannot be deleted.")
