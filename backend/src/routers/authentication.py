import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from pydantic import BaseModel
from pwdlib import PasswordHash

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)

from src.schemas.common import Tags, Token
from src.schemas.user import UserCreate, UserOut
from src.services.auth import create_access_token
from src.services.user import create_user, authenticate_user
from src.services.exceptions import UserAlreadyExsistsError
from src.database import SessionDep

router = APIRouter(
    prefix="/auth",
    tags=[Tags.auth],
)

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: SessionDep) -> Token:
    """Endpoint to authenticate (log in) a user and return an access token."""
    user = authenticate_user(db_session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expiry=60  # Token expires in 60 minutes
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register_user")
async def register_user(user_data: UserCreate, db_session: SessionDep) -> UserOut:
    """Endpoint to register a new user. This is a placeholder and should be implemented with proper validation and error handling."""
    
    try:
        user = create_user(db_session, user_data)
    except UserAlreadyExsistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    return user
