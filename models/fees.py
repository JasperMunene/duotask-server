from . import db
from sqlalchemy_serializer import SerializerMixin


class Fee(db.Model, SerializerMixin):
    __tablename__ = 'fees'

    fee_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50))
    fee_percentage = db.Column(db.Numeric(5, 2))
    fixed_fee = db.Column(db.Numeric(18, 2))
    applicable_conditions = db.Column(db.Text)
