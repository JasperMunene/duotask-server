from . import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class PlatformWallet(db.Model, SerializerMixin):
    __tablename__ = 'platform_wallet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    
    status = db.Column(
        db.String(20),
        nullable=False,
        default='active',
        server_default='active'
    )  # e.g. 'active', 'suspended', 'closed'

    currency = db.Column(
        db.String(5),
        nullable=False,
        default='KES',
        server_default='KES'
    )  # Currency field if supporting multi-currency in future

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=db.func.now()
    )
