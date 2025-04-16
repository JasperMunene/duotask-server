from flask import current_app
from intasend import APIService


class GetFunds:
    def __init__(self, user_id, amount, transaction_id):
        self.user_id = user_id
        self.amount = amount
        self.transaction_id = transaction_id
    
    def post(self):
        
        user_id = self.user_id
        amount = self.amount
        transaction_id = transaction_id
        mpesa_number = self._get_user_mpesa_no(user_id)


        
        
    
    def _get_user_payment_info(self, user_id):
        # Lazy import to avoid circular dependencies
        from models.user_info import UserInfo
        user_info = UserInfo.query.filter_by(id=user_id).first()
        return user_info.mpesa_number if user_info else None