from . import db
from sqlalchemy_serializer import SerializerMixin

class Message(db.Model, SerializerMixin):
    """Message model representing individual messages in a conversation"""
    __tablename__ = 'message'

    # Exclude back-references to avoid recursion
    serialize_rules = ('-conversation', '-sender_user', '-reciever_user')

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    reciever_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, default="sent")
    date_time = db.Column(db.DateTime, server_default=db.func.now())
