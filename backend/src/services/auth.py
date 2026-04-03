import jwt
import logging
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from fastapi import Request

from src.services.exceptions import TokenValidationError

logger = logging.getLogger(__name__)

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")
SECRET_KEY = "ec5923f95775cee1b649608757e4be82a403d88b7b4c3c48dee81f212094a784"  # Generated with openssl rand -hex 32
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expiry: int | None = None) -> str:
    to_encode = data.copy()

    # Set expiration timestamp
    if expiry:
        expire_delta = timedelta(minutes=expiry)
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)  # Default to 30 minutes if no expiry is provided

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None


def token_required(request: Request) -> dict | None:
    """Utility function to extract and validate the access token from the request cookies."""
    token = request.cookies.get("access_token")
    
    if not token:
        logger.info("No access token found in cookies")
        raise TokenValidationError("No access token found in cookies.")

    token_payload = decode_access_token(token)

    if not token_payload:
        logger.info("Invalid or expired access token")
        raise TokenValidationError("Invalid or expired access token")

    return token_payload