from . import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class UserRelation(db.Model, SerializerMixin):
    __tablename__ = 'user_relations'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Initiator
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Target

    relation_type = db.Column(db.String(50), nullable=False)  # e.g. 'favorite', 'blocked', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
