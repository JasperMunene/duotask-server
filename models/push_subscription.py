# models/subscription.py

from . import db
from sqlalchemy_serializer import SerializerMixin

class PushSubscription(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, nullable=False)
