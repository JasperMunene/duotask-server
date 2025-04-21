
import requests
import os

class Mpesa_collect:
    def __init__(self, user_id, transaction_id, mpesa_number, amount, currency, email):
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.mpesa_number = mpesa_number
        self.amount = amount
        self.currency = currency
        self.email = email
        
    def post_push(self):
        print('request recieved')
        phone_number = self.mpesa_number
        amount = str(self.amount)
        email = self.email
        currency = self.currency
        mobile_tarrif = "BUSINESS-PAYS"
        
        data = {
                "amount": amount + "00",
                "email": email,
                "currency": currency,
                "mobile_money": {
                    "phone": phone_number,
                    "provider": "MPESA"
                }
            }     
        key = os.getenv("PAYSTACK_LIVE_SESCRET_KEY")
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
     
        response = requests.post(url, json=data, headers=headers)
        print("Response Body:", response.json())