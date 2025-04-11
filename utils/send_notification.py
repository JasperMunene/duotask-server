from flask import current_app
from extensions import socketio
from models import db
from models import Notification
from utils.send_sms import SendSms

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
                socketio.emit('new_sms', {
                    'notification_id': notification.id,
                    'user_id': user_id,
                    'message': notification.message
                }, room=receiver_sid)

                print(f"notification sent to user {user_id} connected to {receiver_sid}")
            else:
                print(f"user {user_id} not online to be notified")

            # Send SMS if important
            if is_important:
                phone_number = self._get_user_phone(user_id)
                if phone_number:
                    SendSms(phone_number, message).post()
                    print(f"Important notification: SMS sent to {phone_number}")
                else:
                    print("Phone number not found for user")

    def _get_user_phone(self, user_id):
        # Lazy import to avoid circular dependencies
        from models import User
        user = User.query.filter_by(id=user_id).first()
        return user.phone if user else None
