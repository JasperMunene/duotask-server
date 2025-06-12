import json
import base64
import requests
from flask import request, current_app, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from dotenv import load_dotenv
import os
from models import db
from models.user_wallet import Wallet
import re
from decimal import Decimal
from extensions import socketio
from utils.send_notification import Notify
from utils.ledgers.platform import FloatLedger
from models.user import User
from models.wallet_transactions import WalletTransaction
# Load environment variables from .env file
load_dotenv()

# M-Pesa API credentials (loaded from .env file)
MPESA_SHORTCODE = os.getenv("SAFARICOM_SANDBOX_SHORTCODE")
MPESA_PASSKEY = os.getenv("SAFARICOM_SANDBOX_PASSKEY")

# URL for Safaricom API
MPESA_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

# Authentication headers
MPESA_AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
MPESA_CONSUMER_KEY = os.getenv("SAFARICOM_SANDBOX_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("SAFARICOM_SANDBOX_CONSUMER_SECRET")

# The URL M-Pesa will call with the payment status
# CALLBACK_URL = os.getenv("CALLBACK_URL")

class MpesaC2BResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        """Initiate M-Pesa C2B Payment."""
        data = request.get_json()
        phone_number = data.get("phone_number")
        amount = data.get("amount")
        call_back_url = f"https://bgrtfdl5-5000.uks1.devtunnels.ms/payment/mpesa/call_back/{user_id}"
        if not phone_number or not amount:
            return {"message": "Missing phone number or amount"}, 400

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
        
        formated_number = format_phone_number(phone_number)
        # Generate the authorization token
        auth_token = self.get_mpesa_auth_token()
        if not auth_token:
            return {"message": "Failed to get authorization token"}, 500

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        def generate_timestamp():
            # Get the current date and time in the required format
            return datetime.now().strftime("%Y%m%d%H%M%S")
        timestamp = generate_timestamp()
        combined_string = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
        # Encode the combined string in base64
        password = base64.b64encode(combined_string.encode()).decode()
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": formated_number,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": formated_number,
            "CallBackURL": call_back_url,
            "AccountReference": "DUOTASKS.COM",
            "TransactionDesc": "Wallet Funding" 
        }

        # Make the API call to M-Pesa C2B
        response = requests.post(MPESA_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return {"message": "Payment request successfully initiated", "data": response.json()}, 200
        else:
            return {"message": "Failed to initiate payment", "error": response.json()}, 500

    def get_mpesa_auth_token(self):
        """Generate an authentication token for M-Pesa API."""
        auth = base64.b64encode(f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth}"
        }

        response = requests.get(MPESA_AUTH_URL, headers=headers)

        if response.status_code == 200:
            auth_token = response.json().get("access_token")
            return auth_token
        return None


class MpesaCallbackResource(Resource):
    
    def post(self, user_id):
        cache = current_app.cache
        data = request.get_json()
        # user_id = request.get
        try:
            stk = data['Body']['stkCallback']
            merchant_request_id = stk.get('MerchantRequestID')
            checkout_request_id = stk.get('CheckoutRequestID')
            result_code = stk.get('ResultCode')
            

            if result_code == 0:
                result_desc = stk.get('ResultDesc')
                metadata = stk.get('CallbackMetadata', {}).get('Item', [])
                parsed_metadata = {item['Name']: item.get('Value') for item in metadata}
                amount = parsed_metadata.get("Amount")
                amount = Decimal(str(parsed_metadata.get("Amount")))
                transaction_id = parsed_metadata.get("MpesaReceiptNumber")
                transaction_date = parsed_metadata.get("TransactionDate")
                phone_number = parsed_metadata.get("PhoneNumber")
                # You must define how to find user_id from phone_number or transaction ID

                if not user_id:
                    return {"message": "User not found", "phone": phone_number}, 404

                wallet = Wallet.query.filter_by(user_id=user_id).first()

                if not wallet:
                    wallet = Wallet(user_id=user_id)

                if wallet.balance is None:
                    wallet.balance = 0.0

                wallet.balance += amount
                # create a wallet transaction
                new_transaction = WalletTransaction(
                    user_id=user_id,
                    reference_id=transaction_id,
                    amount=amount,
                    transaction_date=datetime.fromtimestamp(transaction_date / 1000) if transaction_date else datetime.utcnow(),
                    transaction_type="credit",
                    transaction_fees=Decimal('0.00'),  # Assuming no fees for this transaction  
                    description = "Wallet Top Up via M-Pesa",
                    status = "success"
                )
                db.session.add(new_transaction)
                db.session.add(wallet)
                db.session.commit()
                
                float = FloatLedger(
                    transaction_id,
                    "in",
                    amount,
                    "mpesa",
                    "float",
                    "float_topup",
                    "completed"
                )
                float.ledge()
                
                
                
                receiver_sid = current_app.cache.get(f"user_sid:{user_id}")
                socketio.emit('payment_received', {
                    "message": "Transaction successful",
                    "transaction_id": transaction_id,
                    "amount": str(amount),
                    "phone_number": phone_number
                }, room=receiver_sid)                
                Notify(user_id=user_id, message=f"Wallet top up of KES {amount} was successfull REF {transaction_id}", source="wallet", sender_id=user_id).post()
                # invalidate wallet
                cache.set(f"user_wallet_{user_id}")
                return {
                    "message": "Transaction successful",
                    "transaction_id": transaction_id,
                    "amount": str(amount),
                    "phone_number": phone_number
                }, 200

            else:
                return {
                    "message": "Transaction failed"
                }, 400

        except Exception as e:
            print(str(e))
            return {"error": str(e)}, 500