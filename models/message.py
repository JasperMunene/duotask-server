from . import db
from sqlalchemy_serializer import SerializerMixin


class Message(db.Model, SerializerMixin):
    """Message model representing individual messages in a conversation"""
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    task_giver = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_doer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, server_default=db.func.now())
    