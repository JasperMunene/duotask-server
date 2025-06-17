import json
import base64
import requests
from flask import request, current_app, jsonify
from flask_restful import Resource
from utils.ledgers.platform import FloatLedger
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from dotenv import load_dotenv
import os
from models import db
from extensions import socketio
from utils.send_notification import Notify  
from models.user_wallet import Wallet
from models.wallet_transactions import WalletTransaction
from models.user import User
import re
from decimal import Decimal

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
INITIATOR_NAME = os.getenv("INITIATOR_NAME")
SECURITY_CREDENTIAL = os.getenv("SECURITY_CREDENTIAL")

class MpesaDisbursmentInit(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        phone = data.get("phone")
        amount = data.get("amount")

        if not phone or not amount:
            return {"message": "Phone and amount are required"}, 400

        try:
            access_token = self.generate_access_token()
        except Exception as e:
            return {"message": f"Access token generation failed: {str(e)}"}, 500

        # Callback URLs (update to your live callback endpoints)
        base_url = "https://bgrtfdl5-5000.uks1.devtunnels.ms/api/mpesa"
        timeout_url = f"{base_url}/disbursment/timeout/{user_id}"
        result_url = f"{base_url}/disbursment/callback/{user_id}"
        def format_phone_number(number):
            # Remove all non-digit characters
            digits = re.sub(r'\D', '', number)

            # Case 1: Starts with +254 or 254
            if re.match(r'^254\d{9}$', digits):
                return digits
            if re.match(r'^254\d{9}$', '254' + digits[-9:]):
                return '254' + digits[-9:]

            # Case 2: Starts with 07 or 01 (local format)
            if re.match(r'^0[17]\d{8}$', digits):
                return '254' + digits[1:]

            # Case 3: Already valid
            if re.match(r'^254\d{9}$', digits):
                return digits

            # Invalid format
            return None
        
        formated_number = format_phone_number(phone)
        payload = {
            "InitiatorName": INITIATOR_NAME,
            "SecurityCredential": SECURITY_CREDENTIAL,
            "CommandID": "BusinessPayment",
            "Amount": amount,
            "PartyA": MPESA_SHORTCODE,
            "PartyB": formated_number,
            "Remarks": "Account withdraw",
            "QueueTimeOutURL": timeout_url,
            "ResultURL": result_url,
            "Occasion": "Payment"
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        b2c_url = "https://api.safaricom.co.ke/mpesa/b2c/v3/paymentrequest"

        try:
            response = requests.post(b2c_url, json=payload, headers=headers)
            response_data = response.json()

            if response_data.get("ResponseCode") == "0":
                return {
                    "message": "Disbursement initiated successfully",
                    "response": response_data
                }, 200
            else:
                return {
                    "message": "MPESA transaction failed",
                    "response": response_data
                }, 400

        except Exception as e:
            return {"message": f"Request failed: {str(e)}"}, 500

    def generate_access_token(self):
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        credentials = f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if "access_token" in data:
            return data["access_token"]
        else:
            raise Exception(data.get("error_description", "No access token returned"))
    
    
def calculate_b2c_charge(amount):
    tariff_table = [
        (1, 49, 0), (50, 100, 0), (101, 500, 5), (501, 1000, 5),
        (1001, 1500, 5), (1501, 2500, 9), (2501, 3500, 9), (3501, 5000, 9),
        (5001, 7500, 11), (7501, 10000, 11), (10001, 15000, 11),
        (15001, 20000, 11), (20001, 25000, 13), (25001, 30000, 13),
        (30001, 35000, 13), (35001, 40000, 13), (40001, 45000, 13),
        (45001, 50000, 13), (50001, 70000, 13), (70001, 250000, 13),
    ]
    for min_amt, max_amt, fee in tariff_table:
        if min_amt <= amount <= max_amt:
            return fee
    return None

class MpesaDisbursmentCallback(Resource):
    def post(self, user_id):
        cache = current_app.cache
        mpesa_response = request.get_json(force=True)

        if 'Result' not in mpesa_response or 'ResultCode' not in mpesa_response['Result']:
            return {'message': 'Invalid M-PESA callback'}, 400

        try:
            result = mpesa_response['Result']
            transaction_id = result.get('TransactionID')
            params = result.get('ResultParameters', {}).get('ResultParameter', [])
            amount = next((param['Value'] for param in params if param['Key'] == 'TransactionAmount'), 0)
            receiver_info = next((param['Value'] for param in params if param['Key'] == 'ReceiverPartyPublicName'), '')
            match = re.search(r'\d+', receiver_info)

            amount = Decimal(str(amount))
            fee = calculate_b2c_charge(amount)
            total_deduction = Decimal(str(int(amount) + fee if fee is not None else amount))

            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            wallet = Wallet.query.filter_by(user_id=user_id).first()

            if not wallet:
                wallet = Wallet(
                    user_id=user_id,
                    balance=-total_deduction
                )
                db.session.add(wallet)
            else:
                wallet.balance -= total_deduction

            new_transaction = WalletTransaction(
                user_id=user_id,
                reference_id=transaction_id,
                amount=amount,
                transaction_date=datetime.utcnow(),
                transaction_type="debit",
                transaction_fees=Decimal(fee),
                description="Wallet Withdraw to M-Pesa",
                status="success"
            )
            db.session.add(new_transaction)

            db.session.commit()

            # Float ledger entry
            float = FloatLedger(
                transaction_id,
                "out",
                total_deduction,
                "float",
                "user",
                "user_payout",
                "completed"
            )
            float.ledge()

            # Realtime socket notification
            receiver_sid = cache.get(f"user_sid:{user_id}")
            socketio.emit('withdraw_successfully', {
                "message": "Transaction successful",
                "transaction_id": transaction_id,
                "amount": str(amount)
            }, room=receiver_sid)

            # Send platform notification
            Notify(
                user_id=user_id,
                message=f"Withdraw of KES {amount} was successful. M-Pesa ref: {transaction_id}",
                source="wallet",
                sender_id=user_id
            ).post()

            # Invalidate wallet cache
            cache.delete(f"user_wallet_{user_id}")

            return {
                "message": "Transaction successful",
                "transaction_id": transaction_id,
                "amount": str(total_deduction)
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"M-Pesa disbursement callback failed: {e}", exc_info=True)
            return {
                "message": "Internal server error while processing disbursement"
            }, 500
