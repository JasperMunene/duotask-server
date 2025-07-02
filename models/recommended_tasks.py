from . import db
from sqlalchemy_serializer import SerializerMixin

class RecommendedTasks(db.Model, SerializerMixin):
    __tablename__ = 'recommended_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    reason = db.Column(db.String(255), nullable=True)  # Reason for recommendation
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user = db.relationship('User', backref='recommended_tasks')
    task = db.relationship('Task', backref='recommendations')

    serialize_rules = ('-user', '-task')  # Exclude user and task details in serialization