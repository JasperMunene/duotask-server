import os
import random
import datetime
import uuid
from flask import current_app, make_response, url_for, redirect
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from models import db
from models.user import User
from extensions import bcrypt
from authlib.integrations.flask_client import OAuth
import resend
from typing import Tuple, Dict

# Helper function to generate a 6-digit OTP
def generate_otp() -> str:
    """Generate a 6-digit OTP as a string with leading zeros preserved"""
    return f"{random.randint(100000, 999999)}"

# Signup Resource with OTP functionality
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
                auth_provider='email',
                otp_code=generate_otp(),
                otp_expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                otp_last_sent = datetime.datetime.utcnow(),
                is_verified=False
            )
            db.session.add(new_user)
            db.session.commit()

            # Send OTP email
            otp_email_params = {
                "from": "Grnder <onboarding@grnder.fueldash.net>",
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

# Resource to verify OTP
class VerifyOTPResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True,
                            help="Email is required!")
        parser.add_argument('otp', type=str, required=True,
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

# Login Resource
class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True,
                            help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True,
                            help="Password cannot be blank!")
        parser.add_argument('rememberMe', type=bool, default=False, location='json')
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()

        if not user:
            return {"message": "No user with that email credentials"}, 401

        if not bcrypt.check_password_hash(user.password, args['password']):
            return {"message": "Incorrect password"}, 401

        if not user.is_verified:
            return {"message": "Account not verified"}, 403

        if args['rememberMe']:
            cookie_max_age = 30 * 24 * 60 * 60
        else:
            cookie_max_age = 24 * 60 * 60

        try:
            access_token = create_access_token(identity=str(user.id))
            response = make_response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "image": user.image,
                    "access_token": access_token
                },
                "access_token": access_token
            }, 200)

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=cookie_max_age,
            )
            return response

        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return {"message": "Login failed"}, 500

# Google Oauth Resource
class GoogleOAuth:
    def __init__(self, oauth: OAuth, frontend_url: str):
        self.oauth = oauth
        self.frontend_url = frontend_url
        self.google = self._register_google()  # Store the Google client here

    def _register_google(self):
        """Register and return the Google OAuth client"""
        return self.oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),  # Ensure correct env var name
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid profile email'}
        )

class GoogleLogin(Resource):
    def __init__(self, oauth: GoogleOAuth):
        self.oauth = oauth

    def get(self):
        """Initiate Google OAuth flow"""
        try:
            redirect_uri = url_for('authorize_google', _external=True)
            return self.oauth.google.authorize_redirect(redirect_uri)
        except Exception as e:
            current_app.logger.error(f"Google login initiation failed: {str(e)}")
            return {"message": "Google login unavailable"}, 503

class GoogleAuthorize(Resource):
    def __init__(self, oauth: GoogleOAuth):
        self.oauth = oauth
        self.frontend_url = oauth.frontend_url

    def get(self) -> redirect:
        """Handle Google OAuth callback"""
        try:
            token = self.oauth.google.authorize_access_token()
        except Exception as e:
            current_app.logger.error(f"Error authorizing Google access token: {str(e)}")
            return self._redirect_with_error("Failed to authorize access token")

        # Corrected key to 'userinfo_endpoint' (was missing 'o')
        userinfo_endpoint = self.oauth.google.server_metadata.get('userinfo_endpoint')
        if not userinfo_endpoint:
            current_app.logger.error("Userinfo endpoint not available in server metadata")
            return self._redirect_with_error("Server configuration error")

        try:
            res = self.oauth.google.get(userinfo_endpoint)
            res.raise_for_status()
            user_info = res.json()
        except Exception as e:
            current_app.logger.error(f"Error fetching user info: {str(e)}")
            return self._redirect_with_error("Failed to fetch user information")

        if 'email' not in user_info:
            current_app.logger.error("User info does not contain email")
            return self._redirect_with_error("Email not provided by Google")

        try:
            user = self._get_or_create_user(user_info)
        except Exception as e:
            current_app.logger.error(f"Error creating user: {str(e)}")
            return self._redirect_with_error("Account creation failed")

        return self._create_authorized_response(user)

    def _get_or_create_user(self, user_info: dict) -> User:
        """Get or create user from Google profile"""
        email = user_info['email']
        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                name=user_info.get('name', 'Google User'),
                email=email,
                image=user_info.get('picture'),
                auth_provider='google',
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()

        return user

    def _create_authorized_response(self, user: User) -> redirect:
        """Create final authorized response with JWT"""
        access_token = create_access_token(identity=str(user.id))
        response = redirect(f"{self.frontend_url}/onboarding")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=86400
        )
        return response

    def _redirect_with_error(self, message: str) -> redirect:
        """Redirect to frontend with error message"""
        error_url = f"{self.frontend_url}/login?error={message}"
        return redirect(error_url)

# Resend OTP Resource
class ResendOTPResource(Resource):
    """Handle OTP resend requests with rate limiting"""

    # Cooldown period in seconds (5 minutes)
    RESEND_COOLDOWN = 300

    def post(self) -> Tuple[Dict, int]:
        """
        Resend OTP to user's email
        ---
        parameters:
          - name: email
            in: body
            required: true
            type: string
        responses:
          200:
            description: OTP resent successfully
          400:
            description: Email already verified
          404:
            description: User not found
          429:
            description: Resend request too frequent
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True,
                            help="Email is required!")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user:
            return {"message": "User not found"}, 404

        if user.is_verified:
            return {"message": "Email is already verified"}, 400

        # Rate limiting check
        if self._is_too_frequent(user):
            return {"message": "Please wait before requesting a new OTP"}, 429

        new_otp = generate_otp()
        try:
            user.otp_code = new_otp
            user.otp_expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            user.otp_last_sent = datetime.datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {"message": "Failed to update OTP"}, 500

        self._send_otp_email(user.email, new_otp)
        return {"message": "OTP resent successfully"}, 200

    def _is_too_frequent(self, user: User) -> bool:
        """Check if resend requests are too frequent"""
        if user.otp_last_sent:
            # Use UTC-naive datetime for both values
            now = datetime.datetime.utcnow()
            elapsed = (now - user.otp_last_sent).total_seconds()
            return elapsed < self.RESEND_COOLDOWN
        return False

    def _send_otp_email(self, email: str, otp: str) -> None:
        """Send OTP email using Resend service"""
        try:
            resend.Emails.send({
                "from": "Grnder <onboarding@grnder.fueldash.net>",
                "to": [email],
                "subject": "Your Verification Code",
                "html": f"""
                    <p>Your verification code is: <strong>{otp}</strong></p>
                    <p>This code expires in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                """
            })
        except Exception as e:
            current_app.logger.error(f"Email send failed: {str(e)}")


# Forgot Password Resource
class ForgotPasswordResource(Resource):
    """Handle password reset requests with secure token handling"""

    TOKEN_EXPIRATION = datetime.timedelta(minutes=30)

    def post(self) -> Tuple[Dict, int]:
        """
        Initiate password reset process
        ---
        parameters:
          - name: email
            in: body
            required: true
            type: string
        responses:
          200:
            description: Reset email sent
          404:
            description: User not found
          500:
            description: Failed to send email
        """
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True,
                            help="Email is required!")
        args = parser.parse_args()

        user = User.query.filter_by(email=args["email"]).first()
        if not user:
            return {"message": "If this email exists, we'll send a reset link"}, 200

        try:
            reset_token = self._generate_reset_token()
            user.reset_token = reset_token
            user.reset_expires_at = datetime.datetime.utcnow() + self.TOKEN_EXPIRATION
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {"message": "Failed to generate reset token"}, 500

        if not self._send_reset_email(user.email, reset_token):
            return {"message": "Failed to send reset email"}, 500

        return {"message": "Reset instructions sent to your email"}, 200

    def _generate_reset_token(self) -> str:
        """Generate a secure random token"""
        return uuid.uuid4().hex + uuid.uuid4().hex

    def _send_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email with frontend URL"""
        frontend_url = current_app.config['FRONTEND_URL']
        reset_url = f"{frontend_url}reset-password?token={token}"

        try:
            resend.Emails.send({
                "from": "Grnder <onboarding@grnder.fueldash.net>",
                "to": [email],
                "subject": "Password Reset Request",
                "html": f"""
                    <p>We received a password reset request. Click the link below:</p>
                    <a href="{reset_url}">{reset_url}</a>
                    <p>This link expires in {self.TOKEN_EXPIRATION.seconds // 60} minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                """
            })
            return True
        except Exception as e:
            current_app.logger.error(f"Email send failed: {str(e)}")
            return False


class ResetPasswordResource(Resource):
    """Handle actual password reset with token validation"""

    def post(self) -> Tuple[Dict, int]:
        """
        Complete password reset process
        ---
        parameters:
          - name: token
            in: body
            required: true
            type: string
          - name: password
            in: body
            required: true
            type: string
        responses:
          200:
            description: Password updated
          400:
            description: Invalid/expired token
          404:
            description: User not found
        """
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        user = User.query.filter_by(reset_token=args['token']).first()
        if not user:
            return {"message": "Invalid reset token"}, 400

        if datetime.datetime.utcnow() > user.reset_expires_at:
            return {"message": "Reset link has expired"}, 400

        try:
            user.password = bcrypt.generate_password_hash(args['password']).decode('utf-8')
            user.reset_token = None
            user.reset_expires_at = None
            db.session.commit()
            return {"message": "Password updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset error: {str(e)}")
            return {"message": "Failed to update password"}, 500