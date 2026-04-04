import hashlib
import jwt
import logging
import secrets
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select

from fastapi import Request

from src.services.exceptions import TokenValidationError
from src.models.auth import RefreshToken

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


def hash_refresh_token(raw_token: str) -> str:
    """Hash the raw refresh token using (deterministic) SHA-256."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_refresh_token(user_id: int, db_session: Session) -> str:
    """Create a new refresh token for the given user and store it in the database."""
    raw_token = secrets.token_urlsafe(64)
    token_hash = hash_refresh_token(raw_token)

    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)  # Refresh token valid for 30 days
    )
    db_session.add(db_token)
    db_session.commit()
    db_session.refresh(db_token)
    
    return raw_token


def verify_and_rotate_refresh_token(raw_token: str, db_session: Session) -> int | None:
    """Verify the provided refresh token and rotate it if valid. Returns the user_id if valid, otherwise None."""
    token_hash = hash_refresh_token(raw_token)
    db_token = db_session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()

    if not db_token or db_token.revoked_at is not None or db_token.expires_at < datetime.now(timezone.utc):
        logger.warning("Invalid, revoked, or expired refresh token")
        return None
    
    db_token.revoked_at = datetime.now(timezone.utc)
    db_session.commit()
    return db_token.user_id

    
def revoke_all_refresh_tokens_for_user(user_id: int, db_session: Session) -> None:
    """Revoke all refresh tokens for a given user."""
    tokens = db_session.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),  # type: ignore
        )
    ).all()

    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)
    db_session.commit()


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