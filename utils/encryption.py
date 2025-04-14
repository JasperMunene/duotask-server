# encryption_utils.py
from cryptography.fernet import Fernet
import os

# Generate a key once and store it securely (e.g., in .env)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return fernet.decrypt(data.encode()).decode()
