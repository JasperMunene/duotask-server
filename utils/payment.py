from flask import current_app

from utils.gateways.paystack_mpesa_collect import Mpesa_collect
from utils.gateways.paystack_mpesa_send import Mpesa_send
from models.payment_details import PaymentDetail
from models.user import User

class GetFunds:
    def __init__(self, user_id, amount, transaction_id):
        self.user_id = user_id
        self.amount = amount
        self.transaction_id = transaction_id
    
    def post(self):
        user_id = self.user_id
        amount = self.amount
        transaction_id = self.transaction_id

        # Get payment details
        payment_info = self._get_user_payment_info(user_id)
        
        mpesa_details = payment_info.get("mpesa_details")
        default_method = payment_info.get("default_method")
        email = payment_info.get('email')
        currency = payment_info.get('currency')
        
        if not mpesa_details or not mpesa_details[0].get("mpesa_number"):
            return {"error": "No M-Pesa number found."}, 400
        
        raw_number = mpesa_details[0]["mpesa_number"]

        # Normalize to international format
        if raw_number.startswith("0"):
            mpesa_number = "+254" + raw_number[1:]
        else:
            mpesa_number = raw_number
        
        # You can now proceed with fund collection logic
        if default_method == "mpesa":
            # print(first_name)
            print(f"mpesa number is {mpesa_number}")
            Mpesa_collect(user_id, transaction_id, mpesa_number, amount, currency, email).post_push()

    def _get_user_payment_info(self, user_id):
       
        user = User.query.get(user_id)
        if not user:
            email = "User"
        else:
            email = user.email
        details = PaymentDetail.query.filter_by(user_id=user_id).all()

        card_details = []
        mpesa_details = []
        default_method = None

        for detail in details:
            if detail.card_token:
                card_details.append({
                    "card_token": detail.card_token
                })

            if detail.mpesa_number:
                mpesa_details.append({
                    "mpesa_number": detail.mpesa_number
                })

            if detail.default_method:
                default_method = detail.default_method
            if detail.currency:
                currency = detail.currency
        return {
            "email": email,
            "currency": currency,
            "default_method": default_method,
            "mpesa_details": mpesa_details,
            "card_details": card_details
        }

class SendFunds:
    def __init__(self, user_id, amount, transaction_id):
        self.user_id = user_id
        self.amount = amount
        self.transaction_id = transaction_id
    
    def post(self):
        user_id = self.user_id
        amount = self.amount
        transaction_id = self.transaction_id

        # Get payment details
        payment_info = self._get_user_payment_info(user_id)
        
        mpesa_details = payment_info.get("mpesa_details")
        default_method = payment_info.get("default_method")
        name = payment_info.get('name')
        currency = payment_info.get('currency')
        
        if not mpesa_details or not mpesa_details[0].get("mpesa_number"):
            return {"error": "No M-Pesa number found."}, 400
        
        raw_number = mpesa_details[0]["mpesa_number"]

        print("this is mpesa pay working")
        
        # You can now proceed with fund collection logic
        Mpesa_send(user_id, transaction_id, raw_number, amount, currency, name).post_push()

    def _get_user_payment_info(self, user_id):
       
        user = User.query.get(user_id)
        if not user:
            name = "User"
        else:
            name = user.name
        details = PaymentDetail.query.filter_by(user_id=user_id).all()

        card_details = []
        mpesa_details = []
        default_method = None

        for detail in details:
            if detail.card_token:
                card_details.append({
                    "card_token": detail.card_token
                })

            if detail.mpesa_number:
                mpesa_details.append({
                    "mpesa_number": detail.mpesa_number
                })

            if detail.default_method:
                default_method = detail.default_method
            if detail.currency:
                currency = detail.currency
        return {
            "name": name,
            "currency": currency,
            "default_method": default_method,
            "mpesa_details": mpesa_details,
            "card_details": card_details
        }
