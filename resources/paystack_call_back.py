from flask import request
from flask_restful import Resource
from models import db
import hashlib, hmac, os
from models.user_wallet import Wallet
from decimal import Decimal

class Paystack_callback(Resource):    
    def post(self):
        PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SESCRET_KEY")
        signature = request.headers.get("x-paystack-signature")
        payload = request.get_data()

        # Verify HMAC SHA512 signature
        computed_sig = hmac.new(PAYSTACK_SECRET_KEY.encode(), payload, hashlib.sha512).hexdigest()
        if signature != computed_sig:
            return "Invalid signature", 400

        print("✅ Callback received")
        
        # Load webhook payload
        event = request.get_json()
        print(event)
        if event["event"] == "charge.success":
            data = event["data"]
            reference = data.get("reference")
            amount = Decimal(data.get("amount")) / 100  # Convert minor units (e.g., KES cents) to full units

            # Locate wallet using the reference stored earlier during post_push()
            wallet = Wallet.query.filter_by(collection_ref=reference).first()

            if wallet:
                wallet.balance += amount
                wallet.collection_ref = None  # Clear once used
                db.session.commit()
                print(f"✅ Wallet credited for user_id {wallet.user_id} with {amount} {data.get('currency')}")
            else:
                print(f"⚠️ No wallet found with reference: {reference}")

        return {"status": "success"}, 200
