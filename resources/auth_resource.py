import random
import datetime
from flask import current_app, make_response
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from models import db, User
from extensions import bcrypt
import resend


def generate_otp() -> str:
    """Generate a 6-digit OTP as a string with leading zeros preserved"""
    return f"{random.randint(100000, 999999)}"


class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help="Name cannot be blank!")
        parser.add_argument('email', type=str, required=True,
                            help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True,
                            help="Password cannot be blank!")
        args = parser.parse_args()

        # Check for existing user
        if User.query.filter_by(email=args['email']).first():
            return {"message": "User with that email already exists"}, 409

        try:
            hashed_password = bcrypt.generate_password_hash(
                args['password']
            ).decode('utf-8')

            # Create new user
            new_user = User(
                name=args['name'],
                email=args['email'],
                password=hashed_password,
                otp_code=generate_otp(),
                otp_expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                is_verified=False
            )
            db.session.add(new_user)
            db.session.commit()

            # Send OTP email
            otp_email_params = {
                "from": "Gig App <onboarding@hello.fueldash.net>",
                "to": [args['email']],
                "subject": "Verify Your Email Address",
                "html": f"""<p>Your verification code is <strong>{new_user.otp_code}</strong>. 
                          It expires in 10 minutes.</p>"""
            }
            resend.Emails.send(otp_email_params)

            return {
                "message": "User created. Please verify your email.",
                "user_id": new_user.id
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Signup error: {str(e)}")
            return {"message": "Registration failed"}, 500


class VerifyOTPResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True,
                            help="Email is required!")
        parser.add_argument('otp', type=str, required=True,  # Changed to string
                            help="OTP code is required!")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user:
            return {"message": "User not found"}, 404

        if user.is_verified:
            return {"message": "Account already verified"}, 400

        if datetime.datetime.utcnow() > user.otp_expires_at:
            return {"message": "OTP has expired"}, 400

        if user.otp_code != args['otp']:  # Direct string comparison
            return {"message": "Invalid OTP code"}, 400

        try:
            user.is_verified = True
            user.otp_code = None
            user.otp_expires_at = None
            db.session.commit()

            access_token = create_access_token(identity=str(user.id))
            response = make_response({
                "message": "Email verified successfully",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            }, 200)

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=86400
            )
            return response

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Verification error: {str(e)}")
            return {"message": "Verification failed"}, 500


class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True,
                            help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True,
                            help="Password cannot be blank!")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()

        if not user:
            return {"message": "Invalid credentials"}, 401

        if not bcrypt.check_password_hash(user.password, args['password']):
            return {"message": "Invalid credentials"}, 401

        if not user.is_verified:
            return {"message": "Account not verified"}, 403

        try:
            access_token = create_access_token(identity=user.id)
            response = make_response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "image": user.image
                }
            }, 200)

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=86400
            )
            return response

        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return {"message": "Login failed"}, 500