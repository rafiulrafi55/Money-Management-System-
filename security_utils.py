import hashlib
import json
import os
from cryptography.fernet import Fernet

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password: str, stored_hash: str) -> bool:
    return hashlib.sha256(input_password.encode()).hexdigest() == stored_hash

KEY_FILE = os.path.join(os.getenv("APPDATA"), "Monefy", "secret.key")

def load_key():
    folder = os.path.dirname(KEY_FILE)
    os.makedirs(folder, exist_ok=True)

    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

fernet = Fernet(load_key())

def encrypt_json(data: dict) -> bytes:
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_json(data: bytes) -> dict:
    return json.loads(fernet.decrypt(data).decode())
