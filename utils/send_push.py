from pyfcm import FCMNotification
import os

class SendPush:
    def __init__(self, device_token, message_title, message_body):
        self.device_token = device_token
        self.message_title = message_title
        self.message_body = message_body

    def send_push(self):
        try:
            # Initialize the FCM push service with your Firebase server key
            push_service = FCMNotification(api_key=os.getenv("FIREBASE_SERVER_KEY"))

            # Send push to a single device
            result = push_service.notify_single_device(
                registration_id=self.device_token,
                message_title=self.message_title,
                message_body=self.message_body
            )

            print("Push sent:", result)
            return True
        except Exception as e:
            print("Push failed:", repr(e))
            return False
