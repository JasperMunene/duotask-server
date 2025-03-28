import requests
import os


class SendSms:
    def __init__(self, phone, message):
        self.phone = str(phone)
        self.message = message

    def post(self):
        # Remove leading zero(s) from phone number
        formatted_phone = self.phone.lstrip('0')
        full_phone = f'254{formatted_phone}'

        # URL for SMS portal
        url = "https://smsportal.hostpinnacle.co.ke/SMSApi/send"

        # Prepare payload
        payload = {
            'userid': os.getenv("SMS_USER_ID"),
            'password': os.getenv("SMS_PASSWORD"),
            'mobile': full_phone,
            'msg': self.message,
            'senderid': 'Intacom',
            'msgType': 'text',
            'duplicatecheck': 'true',
            'output': 'json',
            'sendMethod': 'quick'
        }

        # Headers
        headers = {
            'apikey': os.getenv("SMS_API_KEY"),
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return {"success": "success"}
        except requests.HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}"}
        except requests.RequestException as e:
            return {"error": str(e)}
