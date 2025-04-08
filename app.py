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
from resources.task_resource import TaskResource, SingleTaskResource
from resources.conversation_resource import ConversationResource, OlderMessages
from resources.bid_resource import BidsResource
from datetime import timedelta
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth
from socket_events import handle_connect, handle_disconnect, handle_message_read, handle_mark_all_delivered, handle_send_message, handle_typing
import threading

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
        CELERY_BROKER_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER = 'json',
        CELERY_ACCEPT_CONTENT = ['json'],
        CELERY_TIMEZONE = 'UTC',
        CELERY_ENABLE_UTC = True,
        CACHE_DEFAULT_TIMEOUT=300,
        PROFILE_CACHE_TTL=300
    )

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)
    jwt = JWTManager(app)
    socketio.init_app(app, cors_allowed_origins="*")  # Configure CORS for Socket.IO

    # Configure Flask-Caching
    cache = Cache(app)
    app.cache = cache

    # Configure Redis connection
    app.redis = redis.Redis.from_url(
        app.config["CACHE_REDIS_URL"],
        decode_responses=True
    )

    # Set up a lock for category creation to prevent race conditions
    app.category_lock = threading.Lock()

    # Initialize Celery
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    CELERYD_PREFETCH_MULTIPLIER=1,
    app.celery = celery

    # Enable CORS
    CORS(app)

    # Database migrations
    migrate = Migrate(app, db)

    # Initialize OAuth
    oauth = OAuth(app)
    google_oauth = GoogleOAuth(oauth, app.config['FRONTEND_URL'])

    # Setup API resources
    api = Api(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    class HealthCheck(Resource):
        def get(self):
            try:
                app.redis.ping()
                return {"status": "healthy", "redis": "connected"}, 200
            except redis.ConnectionError:
                return {"status": "healthy", "redis": "disconnected"}, 200

    # Register resources
    api.add_resource(HealthCheck, '/health')
    api.add_resource(UserHealthResource, '/health/user')
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
    api.add_resource(TaskResource, '/tasks')
    api.add_resource(SingleTaskResource, '/tasks/<int:task_id>')
    api.add_resource(ConversationResource, '/conversations', '/conversations/<int:user_id>')
    api.add_resource(OlderMessages, '/messages/<int:conversation_id>')

    api.add_resource(BidsResource, '/tasks/<int:task_id>/bids')
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )
else:
    app = create_app()
