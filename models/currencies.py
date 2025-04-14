from . import db
from sqlalchemy_serializer import SerializerMixin


class Currency(db.Model, SerializerMixin):
    __tablename__ = 'currencies'

    currency_code = db.Column(db.String(10), primary_key=True)
    exchange_rate = db.Column(db.Numeric(18, 6))
    currency_name = db.Column(db.String(100))
