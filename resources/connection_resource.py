from flask_socketio import socketio
from flask import current_app, jsonify, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User


class Connection(Resource):
    # @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id :
            return {"message":  "no user_id passed for the session"}, 401
        
        user = User.query.filter_by(id=user_id).first()
        
        if user:
            socketio.emit('connect_user', {'user_id': user_id})
            return {"message": "Connected successfully"}, 200
        else:
            return {"message": "Invalid user_id, connection failed"}, 400