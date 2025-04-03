from flask import Flask
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_caching import Cache
from dotenv import load_dotenv
from flask_cors import CORS
import redis
import os
from models import db
from extensions import bcrypt
from flask_jwt_extended import JWTManager
from resources.auth_resource import SignupResource, VerifyOTPResource, LoginResource, GoogleLogin, GoogleAuthorize, \
    GoogleOAuth, ResendOTPResource, ForgotPasswordResource, ResetPasswordResource
from resources.user_resource import UserProfileResource, UserHealthResource
from resources.task_resource import TaskResource
from resources.conversation_resource import ConversationResource
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
        FRONTEND_URL=os.getenv("FRONTEND_URL", "http://localhost:3000"),
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        CACHE_DEFAULT_TIMEOUT=300,
        PROFILE_CACHE_TTL=300
    )

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)
    jwt = JWTManager(app)

    # Configure Flask-Caching
    cache = Cache(app)
    app.cache = cache  # Explicitly register cache with app

    # Configure direct Redis connection
    app.redis = redis.Redis.from_url(
        app.config["CACHE_REDIS_URL"],
        ssl_cert_reqs=None,
        decode_responses=True
    )

    CORS(app
        #  ,
        #  resources={r"/auth/*": {"origins": app.config['FRONTEND_URL']}},
        #  supports_credentials=True,
        #  allow_headers=["Content-Type", "Authorization"],
        #  methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
         )

    migrate = Migrate(app, db)

    # Initialize OAuth
    oauth = OAuth(app)
    google_oauth = GoogleOAuth(oauth, app.config['FRONTEND_URL'])

    # Setup API resources
    api = Api(app)

    class HealthCheck(Resource):
        def get(self):
            try:
                app.redis.ping()
                return {"status": "healthy", "redis": "connected"}, 200
            except redis.ConnectionError:
                return {"status": "healthy", "redis": "disconnected"}, 200

#Health Resource
    api.add_resource(HealthCheck, '/health')
    api.add_resource(UserHealthResource, '/health/user')

#Auth Resource
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
    api.add_resource(UserProfileResource, '/user/profile')

#Task Resource
    api.add_resource(TaskResource, '/tasks')

# conversatoin Resource
    api.add_resource(ConversationResource, '/conversations', '/conversations/<int:user_id>')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()