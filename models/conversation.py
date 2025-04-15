from . import db
from sqlalchemy_serializer import SerializerMixin

class Conversation(db.Model, SerializerMixin):
    """Conversation model representing exchanges between users"""
    __tablename__ = 'conversation'

    # Exclude messages and user back-references to avoid cycles
    serialize_rules = ('-messages', '-task_giver_user', '-task_doer_user')

    id = db.Column(db.Integer, primary_key=True)
    task_giver = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_doer = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    last_msg_id_giver = db.Column(db.Integer, nullable=True)
    last_msg_id_doer = db.Column(db.Integer, nullable=True)

    # Relationship: messages are loaded dynamically
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade="all, delete-orphan")
