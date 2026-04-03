import logging
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from src.models.user import User, UserCredential
from src.schemas.user import UserOut, UserCreate
from src.services.auth import hash_password, verify_password, DUMMY_HASH
from src.services.exceptions import UserAlreadyExistsError

logger = logging.getLogger(__name__)


def get_user(db_session: Session, user_id: int | None = None, email: str | None = None, username: str | None = None) -> UserOut | None:
    """Get user from the database."""

    if user_id is not None:
        statement = select(User).where(User.id == user_id)
    elif email is not None:
        statement = select(User).where(User.email == email)
    elif username is not None:
        statement = select(User).where(User.username == username)
    else:
        logger.error("get_user called without user_id, email, or username")
        raise ValueError("At least one of user_id, email, or username must be provided")

    result = db_session.exec(statement).first()

    return UserOut.model_validate(result) if result else None


def create_user(db_session: Session, user_data: UserCreate) -> UserOut:
    """Create a new user with a local (email/password) credential."""

    new_user = User(email=user_data.email)
    try:
        db_session.add(new_user)
        db_session.flush()  # Persist to get the generated ID without committing yet

    except IntegrityError as e:
        db_session.rollback()

        if "email" in str(e.orig):
            logger.warning(f"Attempt to create user with existing email {user_data.email}")
            raise UserAlreadyExistsError(f"A user with this email already exists - {user_data.email}") from e

        logger.error(f"Unexpected IntegrityError creating user {user_data.email}: {e}")
        raise

    credential = UserCredential(
        user_id=new_user.id,
        provider="local",
        password_hash=hash_password(user_data.password),
    )
    db_session.add(credential)
    db_session.commit()
    db_session.refresh(new_user)

    return UserOut.model_validate(new_user)


def authenticate_user(db_session: Session, email: str, password: str) -> UserOut | None:
    """Authenticate a user by email and password. Returns the user if credentials are valid."""

    user = db_session.exec(select(User).where(User.email == email)).first()

    if not user:
        logger.warning(f"Authentication failed for email {email}: user not found")
        verify_password(password, DUMMY_HASH)  # Prevent timing attacks
        return None

    credential = db_session.exec(
        select(UserCredential).where(
            UserCredential.user_id == user.id,
            UserCredential.provider == "local",
        )
    ).first()

    if not credential or not credential.password_hash:
        logger.warning(f"Authentication failed for email {email}: no local credential found")
        verify_password(password, DUMMY_HASH)  # Prevent timing attacks
        return None

    if not verify_password(password, credential.password_hash):
        logger.warning(f"Authentication failed for email {email}: invalid password")
        return None

    return UserOut.model_validate(user)
