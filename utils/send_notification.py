from flask import current_app
from extensions import socketio
from models import db
from models.notification import Notification
from utils.send_sms import SendSms
from models.push_subscription import PushSubscription
from utils.send_push import SendPush
import logging

logger = logging.getLogger(__name__)

class Notify:
    def __init__(self, user_id, message, source, is_important=False, sender_id=None):
        self.user_id = str(user_id)
        self.message = message
        self.source = source
        self.is_important = is_important
        self.sender_id = str(sender_id) if sender_id is not None else None

    def post(self):
        notification = None  # Initialize to prevent reference before assignment
        try:
            if self.source != "chat":
                notification = Notification(
                    user_id=self.user_id,
                    message=self.message,
                    source=self.source,
                    sender_id=self.sender_id
                )
                db.session.add(notification)
                db.session.commit()

            with current_app.app_context():
                user_details = self._get_user_details(self.sender_id)
                receiver_sid = current_app.cache.get(f"user_sid:{self.user_id}")

                if receiver_sid:
                    socketio.emit('new_notification', {
                        'notification_id': notification.id if notification else None,
                        'user_id': self.user_id,
                        'user_data': user_details,
                        'message': self.message,
                        'source': self.source
                    }, room=receiver_sid)
                    logger.info(f"Notification sent to user {self.user_id} on socket {receiver_sid}")
                else:
                    logger.info(f"User {self.user_id} not online to receive notification")

                # SMS fallback if important
                if self.is_important:
                    phone_number = self._get_user_phone(self.user_id)
                    if phone_number:
                        SendSms(phone_number, self.message).post()
                        logger.info(f"Important notification SMS sent to {phone_number}")
                    else:
                        logger.info("Phone number not found for user")

                # Push notifications
                subs = PushSubscription.query.filter_by(user_id=self.user_id).all()
                if not subs:
                    logger.info("User hasn't subscribed to push notifications")

                for sub in subs:
                    SendPush(sub.token, "New notification", self.message).send_push()
        except Exception as e:
            logger.error(f"Error sending notification: {e}", exc_info=True)

    def _get_user_details(self, user_id):
        from models.user import User
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return None
        return {
            "name": user.name,
            "profile_url": user.image
        }

    def _get_user_phone(self, user_id):
        from models.user import User
        user = User.query.filter_by(id=user_id).first()
        return user.phone if user else None
