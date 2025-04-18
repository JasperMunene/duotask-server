
from intasend import APIService
import os

class Intasend_Stk:
    def __init__(self, user_id, transaction_id, mpesa_number, amount, currency, first_name):
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.mpesa_number = mpesa_number
        self.amount = amount
        self.currency = currency
        self.first_name = first_name
        
    def post_push(self):
        print('request recieved')
        token = os.getenv("INSTASEND_API_TOKEN")
        publishable_key = os.getenv("INSTASEND_API_KEY")
        phone_number = self.mpesa_number
        amount = int(self.amount)
        first_name = self.first_name
        currency = self.currency
        mobile_tarrif = "BUSINESS-PAYS"
        transaction_id =self.transaction_id
        # https://sandbox.intasend.com/api/
        method = "M-PESA"
        service = APIService(token=token,publishable_key=publishable_key)
        response = service.collect.mpesa_stk_push(
            phone_number=phone_number,
            api_ref = transaction_id,
            # first_name = first_name,
            # method = method,
            # mobile_tarrif = mobile_tarrif,
            # currency = currency,
            amount=amount, 
            narrative="Purchase")
        print(response.text)