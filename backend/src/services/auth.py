import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from sqlmodel import Session

from src.services.user import get_user

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")
SECRET_KEY = "ec5923f95775cee1b649608757e4be82a403d88b7b4c3c48dee81f212094a784"  # Generated with openssl rand -hex 32
ALGORITHM = "HS256"

def authenticate_user(db_session: Session, username: str, password: str) -> dict | None:
    """Authenticate a user with the given username and password."""
    # Placeholder for actual authentication logic
    user = get_user(db_session, username=username)
    if not user:
        verify_password(password, DUMMY_HASH)  # To prevent timing attacks, we verify the password even if the user doesn't exist. We use a dummy password for this purpose.
        return
    if not verify_password(password, user.get("hashed_password", DUMMY_HASH)):  # TODO: Replace with user.hashed_password when actual user model is implemented
        return
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
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