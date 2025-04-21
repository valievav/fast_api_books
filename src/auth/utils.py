import logging
import uuid
from datetime import timedelta, datetime

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from src.config import Config

ACCESS_TOKEN_EXPIRY = 360  # seconds
REFRESH_TOKEN_EXPIRY = 2  # days

password_context = CryptContext(
    schemes=['bcrypt']
)


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    match = password_context.verify(password, hash)
    return match


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {
        'user': user_data,
        'exp': datetime.now() + (expiry or timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
        'jti': str(uuid.uuid4()),
        'refresh': refresh,
    }
    token = jwt.encode(payload=payload,
                       key=Config.JWT_SECRET_KEY,
                       algorithm=Config.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    try:
        token_data = jwt.decode(jwt=token,
                                key=Config.JWT_SECRET_KEY,
                                algorithms=[Config.JWT_ALGORITHM])
        return token_data
    except jwt.PyJWTError as err:
        logging.exception(err)


# url_safe_token for email verification link
salt = 'email-config'
url_safe_token_serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET_KEY,
    salt=salt
)


def create_url_safe_token(data: dict):
    token = url_safe_token_serializer.dumps(data, salt=salt)
    return token


def decode_url_safe_token(token: str):
    try:
        token_data = url_safe_token_serializer.loads(token, salt=salt)
        return token_data
    except Exception as e:
        logging.error(str(e))
