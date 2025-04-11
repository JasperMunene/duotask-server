from flask import current_app, request
from extensions import socketio
from models import db
from models import Notification
class Notify():
    def __init__(self, user_id, message, source):
        self.user_id = str(user_id)
        self.message = message
        self.source = source
        
    def post(self):
        user_id = self.user_id
        message = self.message
        source = self.source

        notification = Notification(
            user_id=user_id,
            message=message,
            source=source
        )
        
        db.session.add(notification)
        db.session.commit()
        
        with current_app.app_context():
        # Check if receiver is online
            receiver_sid = current_app.cache.get(f"user_sid:{user_id}")
            if receiver_sid:
                # Update message status to delivered

                # Emit to receiver
                socketio.emit('new_sms', {
                    'notification_id': notification.id,
                    'user_id': user_id,
                    'message': notification.message
                }, room=receiver_sid)

                print(f"notification sent to user {user_id} connected to {receiver_sid}")
            else:
                print(f"user {user_id} not online to be notified")
                

        