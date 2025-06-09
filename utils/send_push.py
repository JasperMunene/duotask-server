from pyfcm import FCMNotification
import os

class SendPush:
    def __init__(self, device_token, platform, message_title, message_body):
        self.device_token = device_token
        self.platform = platform
        self.message_title = message_title
        self.message_body = message_body

    def send_push(self):
        try:
            push_service = FCMNotification(api_key=os.getenv("FIREBASE_SERVER_KEY"))

            # Optional: Add platform-specific logic
            payload = {
                "registration_id": self.device_token,
                "message_title": self.message_title,
                "message_body": self.message_body
            }

            # Example: Add custom data if needed
            if self.platform in ["android", "web"]:
                payload["data_message"] = {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }

            result = push_service.notify_single_device(**payload)
            print("Push sent:", result)
            return True
        except Exception as e:
            print("Push failed:", repr(e))
            return False
# utils/send_push.py