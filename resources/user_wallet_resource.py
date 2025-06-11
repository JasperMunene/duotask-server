from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user_wallet import Wallet
from models.wallet_transactions import WalletTransaction
from models.payment_details import PaymentDetail
from models.user import User
from datetime import datetime

def mask_mpesa_number(number):
    if not number or len(number) < 4:
        return "****"
    return "*" * (len(number) - 4) + number[-4:]

class UserWalletResource(Resource):
    @jwt_required()
    def get(self):
        """Return wallet balance, currency, payment method (masked), and transaction history."""
        user_id = get_jwt_identity()

        # Cache handling
        cache = current_app.cache
        cached_wallet = cache.get(f"user_wallet_{user_id}")
        if cached_wallet:
            return cached_wallet, 200

        # Wallet
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.session.add(wallet)
            db.session.commit()

        # Payment method
        payment_detail = PaymentDetail.query.filter_by(user_id=user_id).first()
        if payment_detail and payment_detail.default_method == 'mpesa':
            payment_method = 'M-Pesa'
            masked_number = mask_mpesa_number(payment_detail.mpesa_number)
        elif payment_detail and payment_detail.default_method == 'card':
            payment_method = 'Card'
            masked_number = '****'
        else:
            payment_method = 'Unknown'
            masked_number = '****'

        # Transactions
        transactions = WalletTransaction.query \
            .filter_by(wallet_id=wallet.wallet_id) \
            .order_by(WalletTransaction.transaction_date.desc()) \
            .limit(20) \
            .all()

        history = []
        for txn in transactions:
            history.append({
                "date": txn.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if txn.transaction_date else None,
                "amount": float(txn.amount),
                "reference": txn.reference_id,
                "number": masked_number
            })

        response = {
            "balance": float(wallet.balance),
            "currency": wallet.currency or "KES",
            "payment_method": payment_method,
            "masked_number": masked_number,
            "transactions": history
        }

        # Cache for 5 minutes
        cache.set(f"user_wallet_{user_id}", response, timeout=300)

        return response, 200
