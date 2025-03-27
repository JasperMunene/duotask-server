from flask import Flask
from flask_restful import Api, Resource
from flask_migrate import Migrate
from dotenv import load_dotenv
import resend
import os
from models import db
from extensions import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
resend.api_key = os.getenv("RESEND_API_KEY")


# App Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")

#Initialize Extensions
bcrypt.init_app(app)

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Health(Resource):
    def get(self):
        return "Server is up and running"

api.add_resource(Health, '/')
