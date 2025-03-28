from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UserInfo

class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve user profile image and info."""
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        user_info = UserInfo.query.filter_by(user_id=user_id).first()
        
        if not user:
            return {"message": "User not found"}, 400
        
        return {
            "image_url": user.image,
            "user_info": user_info.to_dict() if user_info else None
        }, 200
    
    @jwt_required()
    def post(self):
        """Create or update user profile image and info."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 400
        
        # Only update the image if provided
        if "image_url" in data:
            user.image = data["image_url"]
        
        user_info = UserInfo.query.filter_by(user_id=user_id).first()

        if user_info:
            return {"message": "User info already exists. Use PATCH to update."}, 400
        
        new_info = UserInfo(
            user_id=user_id,
            tagline=data.get("tagline"),
            bio=data.get("bio"),
            rating=data.get("rating"),
            completion_rate=data.get("completion_rate")
        )
        
        db.session.add(new_info)
        db.session.commit()
        
        return {
            "message": "Profile created successfully",
            "image_url": user.image,
            "user_info": new_info.to_dict()
        }, 201
    
    @jwt_required()
    def patch(self):
        """Update user profile image and info."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 400

        # Only update fields if they exist in the request
        if "image_url" in data:
            user.image = data["image_url"]

        user_info = UserInfo.query.filter_by(user_id=user_id).first()
        if user_info:
            if "tagline" in data:
                user_info.tagline = data["tagline"]
            if "bio" in data:
                user_info.bio = data["bio"]
            if "rating" in data:
                user_info.rating = data["rating"]
            if "completion_rate" in data:
                user_info.completion_rate = data["completion_rate"]
        else:
            # If no UserInfo exists, create one with only provided fields
            user_info = UserInfo(
                user_id=user_id,
                tagline=data.get("tagline"),
                bio=data.get("bio"),
                rating=data.get("rating"),
                completion_rate=data.get("completion_rate")
            )
            db.session.add(user_info)

        db.session.commit()
        
        return {
            "message": "Profile updated successfully",
            "image_url": user.image,
            "user_info": user_info.to_dict() if user_info else None
        }, 200
    
    @jwt_required()
    def delete(self):
        """Delete user profile image and info."""
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        user_info = UserInfo.query.filter_by(user_id=user_id).first()
        
        if not user:
            return {"message": "User not found"}, 400
        
        user.image = None  # Clear image
        
        if user_info:
            db.session.delete(user_info)
        
        db.session.commit()
        
        return {"message": "Profile deleted successfully"}, 200
