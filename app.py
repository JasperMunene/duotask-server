from flask import Flask
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_caching import Cache
from dotenv import load_dotenv
from flask_cors import CORS
from celery import Celery
import redis
import os
from models import db
from extensions import bcrypt, socketio
from flask_jwt_extended import JWTManager
from resources.auth_resource import SignupResource, VerifyOTPResource, LoginResource, GoogleLogin, GoogleAuthorize, \
    GoogleOAuth, ResendOTPResource, ForgotPasswordResource, ResetPasswordResource
from resources.user_resource import UserProfileResource, UserHealthResource
from resources.task_resource import TaskResource, SingleTaskResource, TaskStatusResource
from resources.conversation_resource import ConversationResource, OlderMessages, ChatResource
from resources.feedback_resource import Feedback_resource
from resources.bid_resource import BidsResource
from resources.user_relation_resource import UserRelations
from resources.user_wallet_resource import UserWalletResource

from resources.test_resource import TestFloatLedger
from resources.mpesa_top_up import MpesaC2BResource, MpesaCallbackResource
from resources.mpesa_disbursment_resource import MpesaDisbursmentCallback, MpesaDisbursmentInit
from resources.push_notification import SubscribePush
from resources.assignment_resource import TaskAssignResource
from resources.payment_resources import GetGateways, MpesaPaymentResource, TestMpesa, TestPay, CardPaymentResource, CurrencyDetails, VerifyNumber, ChangeDefault
from resources.paystack_call_back import Paystack_callback
from resources.review_resource import ReviewListResource, ReviewResource
from resources.upload_media_resource import ImageUploadResource
from datetime import timedelta
from authlib.integrations.flask_client import OAuth
import threading
import socket_events
# Load environment variables from .env file
load_dotenv()

def create_app():
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)

    # Application configuration
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        RESEND_API_KEY=os.getenv("RESEND_API_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("CONNECTION_STRING"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        FRONTEND_URL=os.getenv("FRONTEND_URL", "http://localhost:3000"),

        # Caching config
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        CACHE_DEFAULT_TIMEOUT=300,
        PROFILE_CACHE_TTL=300,

        # Celery config
        CELERY_BROKER_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE='UTC',
        CELERY_ENABLE_UTC=True,

        # Web Push Notification Keys
        VAPID_PRIVATE_KEY=os.getenv("VAPID_PRIVATE_KEY"),
        VAPID_PUBLIC_KEY=os.getenv("VAPID_PUBLIC_KEY"),
        VAPID_CLAIMS=os.getenv("VAPID_CLAIMS")
    )

    # Initialize core extensions
    bcrypt.init_app(app)                # Password hashing
    db.init_app(app)                    # Database connection
    jwt = JWTManager(app)              # JWT authentication
    socketio.init_app(app, cors_allowed_origins="*")  # Real-time communication

    # Initialize caching and Redis
    cache = Cache(app)
    app.cache = cache
    app.redis = redis.Redis.from_url(app.config["CACHE_REDIS_URL"], decode_responses=True)

    # Lock to prevent race conditions (e.g. when creating categories)
    app.category_lock = threading.Lock()

    # Configure Celery for background tasks
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    app.celery = celery

    # Enable CORS for cross-origin requests
    CORS(app)

    # Database migrations setup
    migrate = Migrate(app, db)

    # Initialize OAuth (Google in this case)
    oauth = OAuth(app)
    google_oauth = GoogleOAuth(oauth, app.config['FRONTEND_URL'])

    # Initialize API and route definitions
    api = Api(app)

    # Custom task base class to allow Flask context in Celery tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Health check endpoint for Redis
    class HealthCheck(Resource):
        def get(self):
            try:
                app.redis.ping()
                return {"status": "healthy", "redis": "connected"}, 200
            except redis.ConnectionError:
                return {"status": "healthy", "redis": "disconnected"}, 200

    # Register all API resources (routes)
    api.add_resource(HealthCheck, '/health')
    api.add_resource(UserHealthResource, '/health/user')

    # Auth routes
    api.add_resource(SignupResource, '/auth/signup')
    api.add_resource(VerifyOTPResource, '/auth/verify-otp')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(GoogleLogin, '/auth/login/google', resource_class_args=[google_oauth])
    api.add_resource(GoogleAuthorize, '/auth/authorize/google', endpoint='authorize_google', resource_class_args=[google_oauth])
    api.add_resource(ResendOTPResource, '/auth/resend-otp')
    api.add_resource(ForgotPasswordResource, '/auth/forgot-password')
    api.add_resource(ResetPasswordResource, '/auth/reset-password')
    
    # upload media resource 
    api.add_resource(ImageUploadResource, '/api/media/upload')
    
    # User routes
    api.add_resource(UserProfileResource, '/user/profile')

    # Task routes
    api.add_resource(TaskResource, '/tasks')
    api.add_resource(SingleTaskResource, '/tasks/<int:task_id>')
    api.add_resource(TaskStatusResource, '/tasks/<int:task_id>/status')
    api.add_resource(TaskAssignResource, '/tasks/<int:task_id>/assign')

    # Messaging and conversation routes
    api.add_resource(ConversationResource, '/conversations', '/conversations/<int:user_id>')
    api.add_resource(OlderMessages, '/messages/<int:conversation_id>')
    api.add_resource(ChatResource, '/chat/<int:conversation_id>')

    # Bidding and user relation routes
    api.add_resource(BidsResource, '/tasks/<int:task_id>/bids')
    api.add_resource(UserRelations, '/user-relations', '/user-relations/<int:other_user_id>')

    # Wallet and payments
    api.add_resource(UserWalletResource, "/wallet")
    api.add_resource(MpesaC2BResource, '/payment/mpesa/initiate')
    api.add_resource(MpesaCallbackResource, '/payment/mpesa/call_back/<int:user_id>')
    api.add_resource(MpesaDisbursmentInit, '/payment/disbursment/')
    
    api.add_resource(MpesaDisbursmentCallback, '/payment/mpesa/disbursment/call_back/<int:user_id>')
    api.add_resource(GetGateways, '/payment/gateways')
    api.add_resource(MpesaPaymentResource, '/payment/mpesa')
    api.add_resource(CardPaymentResource, '/payment/card')
    api.add_resource(VerifyNumber, '/payment/mpesa/verify')
    api.add_resource(ChangeDefault, '/payment/change_default')
    api.add_resource(CurrencyDetails, '/payment/currency')
    api.add_resource(TestMpesa, '/payment/test/collect')
    api.add_resource(TestPay, '/payment/test/pay')
    api.add_resource(Paystack_callback, '/payment/paystack/callback')
    
    # Review routes
    api.add_resource(ReviewListResource, '/reviews', '/reviews/<int:user_id>')
    api.add_resource(ReviewResource, '/reviews/<int:review_id>')
    # Push notification route
    api.add_resource(SubscribePush, '/notification/subscribe')

    # Feedback routes
    api.add_resource(Feedback_resource, '/feedbacks') #post feedback, get /feedback?page={page}&limit={limit}
    
    # testing resources
    api.add_resource(TestFloatLedger, '/api/test/float_ledger')
    return app

# Run the app using     Flask-SocketIO if this file is run directly
if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )
else:
    # For environments like WSGI servers
    app = create_app()
