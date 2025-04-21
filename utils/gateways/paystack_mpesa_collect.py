
import requests
import os
from models.user_wallet import Wallet
from models import db
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
        user_id = self.user_id
        amount = str(self.amount)
        email = self.email
        currency = self.currency
        
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
        url = "https://api.paystack.co/charge"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
     
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        print(response_data)
        if response_data["status"]:
            print("✅ Transaction successfully initiated!")
            print(response_data)
            reference = response_data["data"]["reference"]

            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                wallet = Wallet(user_id=user_id)
                if wallet.balance is None:
                    wallet.balance = 0.0
                # print("user not found")
            
            wallet.collection_ref = reference
            db.session.add(wallet)
            db.session.commit()
            print("Reference:", reference)

        else:
            print("❌ Failed to initiate transaction:", response_data["message"])