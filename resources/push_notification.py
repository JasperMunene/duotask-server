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

        if not user_id or not device_token:
            return {"error": "Missing user_id or token"}, 400

        # Check if token already exists for user
        existing = PushSubscription.query.filter_by(user_id=user_id, token=token).first()
        if not existing:
            token = PushSubscription(user_id=user_id, token=token)
            db.session.add(token)
            db.session.commit()

        return {"message": "Subscribed successfully!"}, 201
    
# class GetPublicKeys(Resource):
#     def get(self):
#         vapid_public_key = current_app.config['VAPID_PUBLIC_KEY']
#         return {"publicKey": vapid_public_key}, 200

# class SendPushNotification(Resource):
#     # @push_bp.route("/notify/<user_id>", methods=["POST"])
#     def post(self,user_id):
#         subs = PushSubscription.query.filter_by(user_id=user_id).all()
#         if not subs:
#             return {"message": "No subscriptions found"}, 404
        
#         for sub in subs:
#             payload = {
#                 "title": "New Notification",
#                 "body": request.json.get("message"),
#             }
#             subscription_info = {
#                 "endpoint": sub.endpoint,
#                 "keys": {
#                     "p256dh": sub.p256dh,
#                     "auth": sub.auth
#                 }
#             }
#             Sendpush(subscription_info, payload).send_push()

#         return {"message": "Notification sent"}, 200
