import logging
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.schemas.user import UserOut, UserCreate
from src.services.auth import hash_password, verify_password, DUMMY_HASH
from src.services.exceptions import UserAlreadyExsistsError

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
    """Create a new user in the database."""

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    try:
        db_session.add(new_user)
        db_session.commit()
    
    except IntegrityError as e:
        db_session.rollback()
        
        if "email" in str(e.orig):
            logger.warning(f"Attempt to create user with existing email {user_data.email}")
            raise UserAlreadyExsistsError(f"A user with this email already exists - {user_data.email}") from e
        
        logger.error(f"Unexpected IntegrityError creating user {user_data.email}: {e}")
        raise
    
    db_session.refresh(new_user)

    return UserOut.model_validate(new_user)


def authenticate_user(db_session: Session, email: str, password: str) -> UserOut | None:
    """Authenticate a user with the given email and password."""
    # Placeholder for actual authentication logic
    user: UserOut | None = get_user(db_session, email=email)
        
    if not user:
        logger.warning(f"Authentication failed for email {email}: user not found")
        verify_password(password, DUMMY_HASH)  # To prevent timing attacks, we verify the password even if the user doesn't exist. We use a dummy password for this purpose.
        return None
    
    valid_password = verify_password(password, _get_user_password_hash(db_session, user.id))
    if not valid_password:
        logger.warning(f"Authentication failed for email {email}: invalid password")
        return None
    
    return user


### Protected functions

def _get_user_password_hash(db_session: Session, user_id: int) -> str:
    """Get the hashed password for a user by ID. This is a protected function and should not be used outside of authentication logic."""
    user = db_session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        logger.error(f"User with ID {user_id} not found when trying to get password hash")
        raise ValueError("User not found")
    return user.hashed_password