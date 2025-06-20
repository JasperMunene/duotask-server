from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db
from models.user import User
from models.user_info import UserInfo

class MpesaNumber(Resource):
    @jwt_required()
    def get(self):
        cache = current_app.cache
        user_id = get_jwt_identity()
        cache_key = f"user:{user_id}:mpesa"
        mpesa_number = cache.get(cache_key)
        if mpesa_number:
            return {"mpesa_number": mpesa_number, "source": "cache"}, 200

        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user or not user.user_info:
            return {"message": "User or M-Pesa number not found."}, 404

        mpesa_number = user.user_info.mpesa_number
        cache.set(cache_key, mpesa_number)
        return {"mpesa_number": mpesa_number, "source": "db"}, 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        cache = current_app.cache
        mpesa_number = data.get('mpesa_number')

        if not mpesa_number:
            return {"message": "M-Pesa number is required."}, 400

        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user:
            return {"message": "User not found."}, 404

        if user.user_info:
            user.user_info.mpesa_number = mpesa_number
        else:
            user_info = UserInfo(user_id=user_id, mpesa_number=mpesa_number)
            db.session.add(user_info)

        db.session.commit()
        cache.delete(f"user_wallet_{user_id}")
        cache.set(f"user:{user_id}:mpesa", mpesa_number)
        return {"message": "M-Pesa number saved."}, 201

    @jwt_required()
    def put(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        mpesa_number = data.get('mpesa_number')
        cache = current_app.cache

        if not mpesa_number:
            return {"message": "New M-Pesa number is required."}, 400

        user = User.query.options(joinedload(User.user_info)).get(user_id)
        if not user or not user.user_info:
            return {"message": "User or M-Pesa record not found."}, 404

        user.user_info.mpesa_number = mpesa_number
        db.session.commit()
        cache.set(f"user:{user_id}:mpesa", mpesa_number)
        cache.delete(f"user_wallet_{user_id}")
        return {"message": "M-Pesa number updated."}, 200

    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        cache = current_app.cache
        user = User.query.options(joinedload(User.user_info)).get(user_id)

        if not user or not user.user_info:
            return {"message": "User or M-Pesa number not found."}, 404

        db.session.delete(user.user_info)
        db.session.commit()
        cache.delete(f"user:{user_id}:mpesa")
        cache.delete(f"user_wallet_{user_id}")
        return {"message": "M-Pesa number deleted."}, 200
