from flask import request
from flask_restful import Resource
from models import db
from models.user import User
from models.payment_details import PaymentDetail
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
from utils.send_sms import SendSms
import random


def is_valid_mpesa_number(number):
    number = str(number)  # Force string
    pattern = r"^(?:\+254|254|0)?(7\d{8}|1\d{8})$"
    return re.match(pattern, number)


class VerifyNumber(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        mpesa_number = data.get("mpesa_number")

        if not is_valid_mpesa_number(mpesa_number):
            return {"error": "Invalid M-Pesa number format"}, 400

        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        first_name = user.name.split()[0]
        otp = str(random.randint(100000, 999999))

        # Check if a payment detail with mpesa already exists for this user
        detail = PaymentDetail.query.filter_by(user_id=user_id).first()

        if detail:
            # Update existing
            # detail.mpesa_number = mpesa_number
            detail.mpesa_otp = otp
        else:
            # Create new
            detail = PaymentDetail(
                user_id=user_id,
                mpesa_otp=otp
            )
            db.session.add(detail)

        db.session.commit()

        # Send SMS
        message = f"Dear {first_name}, your M-Pesa verification code is {otp}"
        SendSms(mpesa_number, message).post()

        return {"message": f"Verification code sent to {mpesa_number}"}, 200

class MpesaPaymentResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()

        mpesa_number = data.get("mpesa_number")
        currency = data.get("currency", "KES")
        otp = data.get("otp")

        if not is_valid_mpesa_number(mpesa_number):
            return {"error": "Invalid M-Pesa number format."}, 400

        if not otp:
            return {"error": "OTP is required."}, 400

        # Fetch the existing detail
        detail = PaymentDetail.query.filter_by(user_id=user_id).first()

        if not detail:
            return {"error": "No verification record found. Please verify number first."}, 404

        # Check if OTP and number match
        if detail.mpesa_otp != otp:
            return {"error": f"invalid otp. {otp}, {detail.mpesa_otp}"}, 400

        # Update the details (if needed)
        detail.mpesa_number = mpesa_number
        detail.date_modified = db.func.now()
        detail.currency = currency
        detail.default_method="mpesa",
        detail.mpesa_otp = None  # Optional: if you want to track verified status

        db.session.commit()

        return {"message": "M-Pesa number verified and details updated.", 
                "payment": {
                    "user_id": detail.user_id,
                    "mobile_number": detail.user_id,
                    "default_method" : detail.mpesa_number
                    }}, 200

class CardPaymentResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        currency = data.get("currency", "KES")
        # Check if the user already has card details
        existing_detail = PaymentDetail.query.filter_by(user_id=user_id).first()

        # If the user already has card details, return an error
        if existing_detail:
            existing_detail.card_number = data.get("card_number", existing_detail.card_number)
            existing_detail.name_holder = data.get("name_holder", existing_detail.name_holder)
            existing_detail.cvc = data.get("cvc", existing_detail.cvc)
            existing_detail.expirery = data.get("expirery", existing_detail.expirery)
            db.session.commit()
            return {"message": "Card details updated successfull", "details": {
                    "card_number": existing_detail.card_number,
                    "name_holder": existing_detail.name_holder,
                    "cvc": "",  # optionally blank for security
                    "expirery": existing_detail.expirery
                } }, 201

        # Create new card payment details
        detail = PaymentDetail(
            user_id=user_id,
            currency = currency,
            default_method="card",
            card_number=data.get("card_number"),
            name_holder=data.get("name_holder"),
            cvc=data.get("cvc"),
            expirery=data.get("expirery")
        )

        db.session.add(detail)
        db.session.commit()
        return {"message": "Card details added successfull", "details": {
                    "card_number": detail.card_number,
                    "name_holder": detail.name_holder,
                    "cvc": "",  # optionally blank for security
                    "expirery": detail.expirery
                } }, 201

    @jwt_required()
    def put(self):
        data = request.get_json()
        user_id = get_jwt_identity()

        # Check if the user already has card details
        existing_detail = PaymentDetail.query.filter_by(user_id=user_id).first()

        if not existing_detail:
            return {"message": "No existing card details found. Please use POST to create new details."}, 404

        # Update the card details
        existing_detail.card_number = data.get("card_number", existing_detail.card_number)
        existing_detail.name_holder = data.get("name_holder", existing_detail.name_holder)
        existing_detail.cvc = data.get("cvc", existing_detail.cvc)
        existing_detail.expirery = data.get("expirery", existing_detail.expirery)

        db.session.commit()
        return {"message":"card edited successfull", "details": {
                    "card_number": existing_detail.card_number,
                    "name_holder": existing_detail.name_holder,
                    "cvc": "",  # optionally blank for security
                    "expirery": existing_detail.expirery
                }}, 200
class ChangeDefault(Resource):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()  # ✅ add parentheses to call the function
        data = request.get_json()
        default_method = data.get("default_method")

        # Optional: Validate input method
        if default_method not in ["mpesa", "card"]:
            return {"message": "Invalid default method. Must be 'mpesa' or 'card'."}, 400

        payment_details = PaymentDetail.query.filter_by(user_id=user_id).first()

        if not payment_details:
            return {"message": "No payment detail found"}, 404

        payment_details.default_method = default_method
        db.session.commit()

        return {"message": f"Default changed to {payment_details.default_method}"}, 200

class CurrencyDetails(Resource):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()  # fixed here
        data = request.get_json()
        currency = data.get('currency')

        if currency not in ['KES', 'UGX', 'USD']:
            return {"message": "Invalid currency used"}, 400

        payment_details = PaymentDetail.query.filter_by(user_id=user_id).first()
        if not payment_details:
            return {"message": "No payment detail found"}, 404

        payment_details.currency = currency
        db.session.commit()
        return {"message": f"Currency updated to {currency}"}

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        payment_details = PaymentDetail.query.filter_by(user_id=user_id).first()
        if not payment_details:
            return {"message": "No payment detail found"}, 404

        return {"currency": payment_details.currency} if payment_details.currency else {"currency": "KES"}
        
        
class GetGateways(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        # Fetch all payment details for the user
        details = PaymentDetail.query.filter_by(user_id=user_id).all()

        if not details:
            return {"message": "No payment details found for this user."}, 404

        card_details = []
        mpesa_details = []
        default_method = None

        for detail in details:
            card_details.append({
                    "card_number": detail.card_number,
                    "name_holder": detail.name_holder,
                    "cvc": "",  # optionally blank for security
                    "expirery": detail.expirery
                })
            
            mpesa_details.append({
                    "mpesa_number": detail.mpesa_number
                })
            default_method = detail.default_method
            if detail.currency:
                currency = detail.currency
            else:
                currency = "KES"
        return {
            "default_method": default_method,
            "mpesa_details": mpesa_details,
            "card_details": card_details,
            "currency": currency
        }

