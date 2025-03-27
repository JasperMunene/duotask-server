import random
import datetime
from flask import current_app, make_response
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import bcrypt
import resend

# Helper function to generate a 6-digit OTP
def generate_otp():
    return random.randint(100000, 999999)

# Signup Resource
class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {"message": "User with that email already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')

        # Create the new user (initially not verified)
        new_user = User(
            name=args['name'],
            email=args['email'],
            password=hashed_password,
            otp_code=generate_otp(),
            otp_expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=10),  # OTP valid for 10 minutes
            is_verified=False  # mark as unverified until OTP is confirmed
        )
        db.session.add(new_user)
        db.session.commit()

        # Send OTP email using Resend
        otp_email_params = {
            "from": "Gig App <onboarding@hello.fueldash.net>",
            "to": [args['email']],
            "subject": "Verify Your Email Address",
            "html": f"<p>Your OTP code is <strong>{new_user.otp_code}</strong>. It expires in 10 minutes.</p>"
        }
        try:
            resend.Emails.send(otp_email_params)
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP email: {str(e)}")
            return {"message": "User created but failed to send OTP email"}, 500

        return {"message": "User created. Please verify your email using the OTP sent.", "user_id": new_user.id}, 201

# New Resource to verify OTP
class VerifyOTPResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email is required!")
        parser.add_argument('otp', type=int, required=True, help="OTP code is required!")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user:
            return {"message": "User not found"}, 404

        # Check if OTP has expired
        if datetime.datetime.utcnow() > user.otp_expires_at:
            return {"message": "OTP has expired"}, 400

        # Check if OTP matches
        if user.otp_code != str(args['otp']):
            return {"message": "Invalid OTP code"}, 400

        # Mark user as verified and clear OTP fields
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        db.session.commit()

        # Optionally, issue an access token now that the user is verified
        access_token = create_access_token(identity=str(user.id))
        response = make_response({
            "message": "Email verified successfully",
            "access_token": access_token
        }, 200)
        expires = datetime.datetime.now() + datetime.timedelta(days=1)
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='None',
            expires=expires,
        )
        return response

class LoginUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
        args = parser.parse_args()
        
        user = User.query.filter_by(email=args['email']).first()

        if not user:
            return {"message": "No user found registered to that email"}, 404

        # Verify password
        if not bcrypt.check_password_hash(user.password, args['password']):
            return {"message": "Invalid email or password!"}, 401

        # Generate JWT token
        access_token = create_access_token(identity=user.id)

        # Create response with user data
        response = make_response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": user.image
            }
        }, 200)

        # Set the access token as an HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevent JavaScript access
            secure=True,    # Only send over HTTPS
            samesite="Lax", # Helps prevent CSRF
            max_age=86400   # Token expires in 1 day (24 hours)
        )


        return response
