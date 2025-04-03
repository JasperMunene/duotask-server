from . import db
from sqlalchemy_serializer import SerializerMixin

class Conversation(db.Model, SerializerMixin):
    """Conversation model representing exchanges between users"""
    __tablename__ = 'conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    task_giver = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_doer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_msg_id_giver = db.Column(db.Integer, nullable=True)
    last_msg_id_doer = db.Column(db.Integer, nullable=True)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic')