import requests

class SendSms:
    def __init__(self, phone, message):
        self.phone = phone
        self.message = message
        
    def post(self):
        message = self.message
        phone = self.phone
        # Remove leading zero from phone number
        formatted_phone = phone.lstrip('0')
        
        # URL for SMS portal
        url = "https://smsportal.hostpinnacle.co.ke/SMSApi/send"
        
        # Prepare payload
        payload = {
            'userid': 'mealscok',
            'password': '-cCtu@NY39w5L8',
            'mobile': f'254{formatted_phone}',
            'msg': message,
            'senderid': 'Intacom',
            'msgType': 'text',
            'duplicatecheck': 'true',
            'output': 'json',
            'sendMethod': 'quick'
        }
        
        # Headers
        headers = {
            'apikey': '58314795da56adcdaae1c219fd48fbf35229e7d5',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Send POST request
            response = requests.post(url, data=payload, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                return {"success": "success"}
            else:
                return {"error": f"HTTP error {response.status_code}: {response.text}"}
        
        except requests.RequestException as e:
            return {"error": str(e)}
