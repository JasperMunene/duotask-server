from . import db
from sqlalchemy_serializer import SerializerMixin

class InternalTransaction(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # task giver
    doer_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default='held')  # 'held', 'released'
    created_at = db.Column(db.DateTime, server_default=db.func.now())
