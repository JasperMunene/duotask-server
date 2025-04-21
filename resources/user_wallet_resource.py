# resources/user_wallet.py

from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user_wallet import Wallet
from models.user import User

class UserWalletResource(Resource):
    @jwt_required()
    def get(self):
        """Return wallet balance."""
        user_id = get_jwt_identity()
        
        # Check cache first
        cache = current_app.cache
        cached_balance = cache.get(f"user_wallet_{user_id}")

        if cached_balance:
            return {"balance": cached_balance}, 200
        
        # If not in cache, get from database
        wallet = Wallet.query.filter_by(user_id=user_id).first()

        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.session.add(wallet)
            db.session.commit()

        # Cache the wallet balance for 5 minutes
        cache.set(f"user_wallet_{user_id}", wallet.balance, timeout=300)

        return {"balance": wallet.balance}, 200

    @jwt_required()
    def post(self):
        """
        Top-up wallet.
        Body: { "amount": 100.0 }
        """
        data = request.get_json()
        amount = data.get("amount", 0.0)
        if amount <= 0:
            return {"message": "Invalid amount"}, 400

        user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=user_id).first()

        if not wallet:
            wallet = Wallet(user_id=user_id)
        if wallet.balance is None:
            wallet.balance = 0.0

        wallet.balance += amount
        db.session.add(wallet)
        db.session.commit()

        # Invalidate cache after update
        cache = current_app.cache
        cache.delete(f"user_wallet_{user_id}")

        return {"message": "Wallet topped up", "balance": wallet.balance}, 200

    @jwt_required()
    def put(self):
        """
        Withdraw funds.
        Body: { "amount": 50.0 }
        """
        data = request.get_json()
        amount = data.get("amount", 0.0)
        if amount <= 0:
            return {"message": "Invalid amount"}, 400

        user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=user_id).first()

        if not wallet or wallet.balance < amount:
            return {"message": "Insufficient balance"}, 400

        wallet.balance -= amount
        db.session.commit()

        # Invalidate cache after update
        cache = current_app.cache
        cache.delete(f"user_wallet_{user_id}")

        return {"message": "Withdrawal successful", "balance": wallet.balance}, 200
