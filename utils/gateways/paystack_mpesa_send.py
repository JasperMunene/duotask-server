
import requests
import os
from models.user_wallet import Wallet
from models import db
class Mpesa_send:
    def __init__(self, user_id, transaction_id, mpesa_number, amount, currency, name):
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.mpesa_number = mpesa_number
        self.amount = amount
        self.currency = currency
        self.name = name
        
    def post_push(self):
        print('request recieved')
        phone_number = self.mpesa_number
        user_id = self.user_id
        amount = str(self.amount)
        name = self.name
        currency = self.currency
        
        data = {
            "type": "mobile_money",
            "name": name,
            "account_number": phone_number,  # Phone number in intl format
            "bank_code": "MPESA",              # Mobile money provider
            "currency": currency
        }
        key = os.getenv("PAYSTACK_LIVE_SESCRET_KEY")
        url = "https://api.paystack.co/transferrecipient"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
     
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        if response_data["status"]:
            print("✅ Transaction successfully initiated!")
            recipient_code = response_data["data"]["recipient_code"]
            urls = "https://api.paystack.co/transfer"

            datas = {
                "source": "balance",
                "amount": amount + "00",  # Amount in kobo (so 50000 = KES 500.00)
                "recipient": recipient_code,
                "reason": "Payout to M-PESA"
            }

            res = requests.post(urls, json=datas, headers=headers)
            responce_d = res.json()
            print(responce_d)
            if responce_d["status"]:
                reference = response_data["data"]["reference"]

                wallet = Wallet.query.filter_by(user_id=user_id).first()
                if not wallet:
                    wallet = Wallet(user_id=user_id)
                    if wallet.balance is None:
                        wallet.balance = 0.0
                    # print("user not found")
                
                wallet.disbursment_ref = reference
                db.session.add(wallet)
                db.session.commit()
                print("Reference:", reference)
                
            
            

        else:
            print("❌ Failed to initiate transaction:", response_data["message"])