from flask import Flask
from flask_restful import Api, Resource
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import resend
import os
from models import db
from extensions import bcrypt
from flask_jwt_extended import JWTManager
from resources.auth_resource import SignupResource, VerifyOTPResource, LoginResource, GoogleLogin, GoogleAuthorize, \
    GoogleOAuth, ResendOTPResource, ForgotPasswordResource, ResetPasswordResource
from resources.user_resource import Profile
from datetime import timedelta
from authlib.integrations.flask_client import OAuth

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Configure app
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        RESEND_API_KEY=os.getenv("RESEND_API_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("CONNECTION_STRING"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        FRONTEND_URL=os.getenv("FRONTEND_URL", "http://localhost:3000")
    )

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)
    jwt = JWTManager(app)

    CORS(app,
         resources={r"/auth/*": {"origins": app.config['FRONTEND_URL']}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
         )

    migrate = Migrate(app, db)

    # Initialize OAuth
    oauth = OAuth(app)
    google_oauth = GoogleOAuth(oauth, app.config['FRONTEND_URL'])

    # Setup API resources
    api = Api(app)
    api.add_resource(HealthCheck, '/health')
    api.add_resource(SignupResource, '/auth/signup')
    api.add_resource(VerifyOTPResource, '/auth/verify-otp')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(GoogleLogin, '/auth/login/google', resource_class_args=[google_oauth])
    api.add_resource(GoogleAuthorize, '/auth/authorize/google',
                     endpoint='authorize_google',
                     resource_class_args=[google_oauth])
    api.add_resource(ResendOTPResource, '/auth/resend-otp')
    api.add_resource(ForgotPasswordResource, '/auth/forgot-password')
    api.add_resource(ResetPasswordResource, '/auth/reset-password')
    api.add_resource(Profile, '/user/profile')


class HealthCheck(Resource):
    def get(self):
        return {"status": "healthy"}, 200


if __name__ == '__main__':
    app = create_app()
    app.run()
