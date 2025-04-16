from flask import current_app

from utils.gateways.intasend_stk_push import Intasend_Stk

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
        first_name = payment_info.get('first_name')
        currency = payment_info.get('currency')
        if not mpesa_details or not mpesa_details[0].get("mpesa_number"):
            return {"error": "No M-Pesa number found."}, 400
        
        mpesa_number = mpesa_details[0]["mpesa_number"]
        
        # You can now proceed with fund collection logic
        if default_method == "mpesa":
            Intasend_Stk(user_id, transaction_id, mpesa_number, amount, currency, first_name)

    def _get_user_payment_info(self, user_id):
        from models.payment_details import PaymentDetail
        from models.user import User
        user = User.query.get(user_id)
        first_name = user.name.split()[0]
        details = PaymentDetail.query.filter_by(user_id=user_id).all()

        card_details = []
        mpesa_details = []
        default_method = None

        for detail in details:
            if detail.card_number:
                card_details.append({
                    "card_number": detail.card_number,
                    "name_holder": detail.name_holder,
                    "cvc": "",  # keep blank for security
                    "expirery": detail.expirery
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
            "fist_name": first_name,
            "currency": currency,
            "default_method": default_method,
            "mpesa_details": mpesa_details,
            "card_details": card_details
        }
