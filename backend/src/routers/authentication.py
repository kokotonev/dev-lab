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
from src.services.auth import authenticate_user, create_access_token
from src.database import SessionDep

router = APIRouter(
    prefix="/auth",
    tags=[Tags.auth],
)

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: SessionDep) -> Token:

    user = authenticate_user(db_session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(
        data={"sub": user.get("username")},  # TODO: Replace with user.username when actual user model is implemented
        expiry=60  # Token expires in 60 minutes
    )

    return Token(access_token=access_token, token_type="bearer")