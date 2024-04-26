import jwt
import os
import datetime

from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Automate loading environment variables in Python script, make them accessible to the project
load_dotenv()

def get_PEM_private_key():
    # Load the PRIVATE_KEY in PEM-formatted string from .env to bytes
    pem_bytes = (os.getenv('PRIVATE_KEY', "")).encode() 
    return pem_bytes

def get_RSA_private_key():
    # Deserializes/Loads the private key from PEM-formatted bytes to an RSA private key object, so we could perform cryptographic operations, such as signing data
    private_key = serialization.load_pem_private_key(
        get_PEM_private_key(), password=None, backend=default_backend()
    )
    return private_key

def get_RSA_public_key():
    # Get the corresponding RSA public key object from private_key
    public_key = get_RSA_private_key().public_key()
    return public_key

def get_PEM_public_key():
    # Serialize the public key from RSA object to PEM format, to verify digital signatures
    pem_bytes = (get_RSA_public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )).decode()
    return pem_bytes