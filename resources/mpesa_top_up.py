import json
import base64
import requests
from flask import request, current_app, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime
from dotenv import load_dotenv
import os
from models import db
from models.user_wallet import UserWallet
# Load environment variables from .env file
load_dotenv()

# M-Pesa API credentials (loaded from .env file)
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")

# URL for Safaricom API
MPESA_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

# Authentication headers
MPESA_AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")

# The URL M-Pesa will call with the payment status
# CALLBACK_URL = os.getenv("CALLBACK_URL")

class MpesaC2BResource(Resource):
    
    @jwt_required()
    def post(self, user_id):
        """Initiate M-Pesa C2B Payment."""
        data = request.get_json()
        phone_number = data.get("phone_number")
        amount = data.get("amount")
        call_back_url = f"https://bgrtfdl5-5000.uks1.devtunnels.ms/api/payment/mpesa/call_back?user_id={user_id}"
        if not phone_number or not amount:
            return {"message": "Missing phone number or amount"}, 400

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
            "PartyA": phone_number,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": call_back_url,
            "AccountReference": "CompanyXLTD",
            "TransactionDesc": "Payment of X" 
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
    
    def post(self):
        """Handle the callback from M-Pesa."""
        # Get the data sent by M-Pesa (transaction status)
        data = request.get_json()
        user_id = request.args.get('user_id')
        # Log or process the data as needed
        print(f"Callback Data: {json.dumps(data, indent=2)}")

        # Check the response and update the transaction status in your database
        # Example: You can check for success and update a payment status
        if data.get("ResultCode") == 0:  # Success
            transaction_id = data.get("TransID")
            phone_number = data.get("MSISDN")
            amount = data.get("Amount")
            wallet = UserWallet.query.filter_by(user_id=user_id).first()

            if not wallet:
                wallet = UserWallet(user_id=user_id)
            if wallet.balance is None:
                wallet.balance = 0.0

            wallet.balance += amount

            wallet.balance += amount
            db.session.add(wallet)
            db.session.commit()
            # Update your payment status here in the database or take necessary action

            return {"message": "Transaction successful", "data": data}, 200
        
        else:
            return {"message": "Transaction failed", "data": data}, 400
