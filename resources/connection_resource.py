from flask import request
from flask_restful import Resource
from extensions import socketio  # ✅ Import socketio from extensions.py
from models.user import User  

class UserConnection(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return {"message": "No user_id provided"}, 400

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "Invalid user_id"}, 404

        socketio.emit('user_connected', {'user_id': user_id})
        return {"message": "User connected successfully"}, 200

class UserDisconnection(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return {"message": "No user_id provided"}, 400

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "Invalid user_id"}, 404

        socketio.emit('user_disconnected', {'user_id': user_id})
        return {"message": "User disconnected successfully"}, 200
