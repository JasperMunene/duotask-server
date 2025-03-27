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
from resources.auth_resource import SignupResource, VerifyOTPResource, LoginUser
from datetime import timedelta


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
resend.api_key = os.getenv("RESEND_API_KEY")
# App Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
SQLALCHEMY_TRACK_MODIFICATIONS = False

#Initialize Extensions
bcrypt.init_app(app)

CORS(app,
     resources={r"/auth/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     )

migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)

class HealthCheck(Resource):
    """Endpoint for service health verification"""
    def get(self):
        """Return service status"""
        return {"status": "healthy", "service": "user-service"}, 200


# API resource registration
api.add_resource(HealthCheck, '/health')

# Auth Resource
api.add_resource(SignupResource, '/auth/signup')
api.add_resource(VerifyOTPResource, '/auth/verify-otp')
api.add_resource(LoginUser, '/auth/login')
