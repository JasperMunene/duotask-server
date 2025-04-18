from flask import current_app
from extensions import socketio
from models import db
from models.notification import Notification
from utils.send_sms import SendSms
from models.push_subscription import PushSubscription
from utils.send_push import SendPush
import logging

logger = logging.getLogger(__name__)

class Notify():
    def __init__(self, user_id, message, source, is_important=False):
        self.user_id = str(user_id)
        self.message = message
        self.source = source
        self.is_important = is_important
        
    def post(self):
        user_id = self.user_id
        message = self.message
        source = self.source
        is_important = self.is_important

        # Save notification
        notification = Notification(
            user_id=user_id,
            message=message,
            source=source
        )
        
        db.session.add(notification)
        db.session.commit()
        
        with current_app.app_context():
            # Check if user is online
            receiver_sid = current_app.cache.get(f"user_sid:{user_id}")
            if receiver_sid:
                # Emit to receiver
                socketio.emit('new_notification', {
                    'notification_id': notification.id,
                    'user_id': user_id,
                    'message': notification.message,
                    'source': notification.source
                }, room=receiver_sid)

                logger.info(f"notification sent to user {user_id} connected to {receiver_sid}")
            else:
                logger.info(f"user {user_id} not online to be notified")

            # Send SMS if important
            if is_important:
                phone_number = self._get_user_phone(user_id)
                if phone_number:
                    SendSms(phone_number, message).post()
                    logger.info(f"Important notification: SMS sent to {phone_number}")
                else:
                    logger.info("Phone number not found for user")
            
            # send push notification
            subs = PushSubscription.query.filter_by(user_id=user_id).all()
            if not subs:
                logger.info("user hasn't subscribed to notification")
            
            for sub in subs:
                device_token = sub.token
                message_title = "New notification"
                message_body = message
                SendPush(device_token, message_title, message_body).send_push()

    def _get_user_phone(self, user_id):
        # Lazy import to avoid circular dependencies
        from models.user import User
        user = User.query.filter_by(id=user_id).first()
        return user.phone if user else None
