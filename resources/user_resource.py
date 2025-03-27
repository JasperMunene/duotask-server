from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserInfo

class Profile(Resource):
    @jwt_required()
    def get(self):
        """Retrieve user info."""
        user_id = get_jwt_identity()
        data = UserInfo.query.filter_by(user_id=user_id).first()
        if not data:
            return {"message": "User info not found"}, 404
        return data.to_dict(), 200

    @jwt_required()
    def post(self):
        """Create new user info."""
        user_id = get_jwt_identity()
        if UserInfo.query.filter_by(user_id=user_id).first():
            return {"message": "User info already exists"}, 400
        
        data = request.get_json()
        new_info = UserInfo(
            user_id=user_id,
            tagline=data.get("tagline"),
            bio=data.get("bio"),
            rating=data.get("rating", 0.0),
            completion_rate=data.get("completion_rate", 0.0)
        )
        db.session.add(new_info)
        db.session.commit()
        return new_info.to_dict(), 201

    @jwt_required()
    def put(self):
        """Update user info."""
        user_id = get_jwt_identity()
        data = UserInfo.query.filter_by(user_id=user_id).first()
        if not data:
            return {"message": "User info not found"}, 404
        
        req_data = request.get_json()
        data.tagline = req_data.get("tagline", data.tagline)
        data.bio = req_data.get("bio", data.bio)
        data.rating = req_data.get("rating", data.rating)
        data.completion_rate = req_data.get("completion_rate", data.completion_rate)
        
        db.session.commit()
        return data.to_dict(), 200

    @jwt_required()
    def delete(self):
        """Delete user info."""
        user_id = get_jwt_identity()
        data = UserInfo.query.filter_by(user_id=user_id).first()
        if not data:
            return {"message": "User info not found"}, 404
        
        db.session.delete(data)
        db.session.commit()
        return {"message": "User info deleted successfully"}, 200
