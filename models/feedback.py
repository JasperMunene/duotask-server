from . import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class Feedback(db.Model, SerializerMixin):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
