from . import db
from sqlalchemy_serializer import SerializerMixin
# import datetime


class PaymentDetail(db.Model, SerializerMixin):
    __tablename__ = 'payment_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    default_method = db.Column(db.String(50))  # 'card' or 'mpesa'
    
    # Mpesa details
    mpesa_number = db.Column(db.String(20), nullable=True)
    
    # Card details
    card_number = db.Column(db.String(20), nullable=True)
    name_holder = db.Column(db.String(100), nullable=True)
    cvc = db.Column(db.String(10), nullable=True)
    expirery = db.Column(db.String(10), nullable=True)  # Format: MM/YY or YYYY-MM
    
    mpesa_otp = db.Column(db.Integer, nullable=True)

    date_added = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    date_modified = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    # Optional: relationship to user model
    user = db.relationship("User", back_populates="payment_details", passive_deletes=True)
