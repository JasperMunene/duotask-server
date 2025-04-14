from . import db
from sqlalchemy_serializer import SerializerMixin

class EscrowAction(db.Model, SerializerMixin):
    __tablename__ = 'escrow_actions'

    action_id = db.Column(db.Integer, primary_key=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey('escrow.escrow_id'), nullable=False)
    action_type = db.Column(db.String(50))
    action_date = db.Column(db.DateTime)
    comments = db.Column(db.Text)

    escrow = db.relationship('Escrow', backref='actions')
