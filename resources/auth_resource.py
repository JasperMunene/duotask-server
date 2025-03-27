from flask import current_app, request
from flask_restful import Resource, reqparse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from models import db, User
from extensions import bcrypt
import resend

# Helper function to create the serializer
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

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
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate a token that includes the user id
        serializer = get_serializer()
        verification_token = serializer.dumps({'user_id': str(new_user.id)})
        # Build verification link (adjust the URL to your frontend/route)
        verification_link = f"http://localhost:3000/verify-email?token={verification_token}"
        verification_email_params = {
            "from": "Gig App <onboarding@hello.fueldash.net>",
            "to": [args['email']],
            "subject": "Verify Your Email Address",
            "html": f"<p>Please verify your email address by clicking the following link: "
                    f"<a href='{verification_link}'>Verify Email</a>. "
                    f"This link will expire in 15 minutes.</p>"
        }
        try:
            resend.Emails.send(verification_email_params)
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return {"message": "User created but failed to send verification email"}, 500

        return {"message": "User created. Please check your email to verify your account.", "user_id": new_user.id}, 201

# Verification Resource
class VerifyEmailResource(Resource):
    def get(self):
        token = request.args.get('token')
        if not token:
            return {"message": "Missing token"}, 400

        serializer = get_serializer()
        try:
            # The max_age is set to 900 seconds (15 minutes)
            data = serializer.loads(token, max_age=900)
        except SignatureExpired:
            return {"message": "Token has expired. Please request a new verification email."}, 400
        except BadSignature:
            return {"message": "Invalid token. Verification failed."}, 400

        user_id = data.get('user_id')
        if not user_id:
            return {"message": "Invalid token payload."}, 400

        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found."}, 404

        # Mark the user as verified
        user.is_verified = True
        db.session.commit()
        return {"message": "Email successfully verified."}, 200
