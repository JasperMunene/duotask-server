# routes/push.py

from flask import request,  current_app
import os
from flask_restful import Resource
from models.push_subscription import PushSubscription
from models import db
import base64


class SubscribePush(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        device_token = data.get("token")
        platform = data.get("platform", "web")  # Default to 'web' if not provided

        if not user_id or not device_token:
            return {"error": "Missing user_id or token"}, 400

        # Check if token already exists for user
        existing = PushSubscription.query.filter_by(user_id=user_id, token=token).first()
        if not existing:
            token = PushSubscription(user_id=user_id, token=token, platform=platform)
            db.session.add(token)
            db.session.commit()

        return {"message": "Subscribed successfully!"}, 201
    