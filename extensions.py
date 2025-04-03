from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

bcrypt = Bcrypt()
