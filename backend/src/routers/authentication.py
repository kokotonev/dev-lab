from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from src.schemas.common import Tags
from src.schemas.user import UserCreate, UserOut, LoginRequest
from src.services.auth import (
    create_access_token, 
    decode_access_token,
    token_required, 
    create_refresh_token, 
    verify_and_rotate_refresh_token,
    revoke_all_refresh_tokens_for_user,
)
from src.services.user import create_user, authenticate_user
from src.services.exceptions import UserAlreadyExistsError
from src.database import SessionDep

router = APIRouter(
    prefix="/auth",
    tags=[Tags.auth],
)

@router.get("/status")
async def auth_status(token_payload: Annotated[dict, Depends(token_required)]) -> dict[str, str | None]:
    """Endpoint to check the authentication status of the current user."""
    return {"user_id": token_payload.get("sub")}


@router.post("/refresh")
async def refresh_access_token(request: Request, response: Response, db_session: SessionDep) -> dict[str, str]:
    """Endpoint to refresh the access token using a valid refresh token."""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = verify_and_rotate_refresh_token(refresh_token, db_session)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    new_access_token = create_access_token(
        data={"sub": str(user_id)},
        expiry=15  # Token expires in 15 minutes
    )

    new_refresh_token = create_refresh_token(user_id, db_session)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=15 * 60,  # Cookie expires in 15 minutes
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # Cookie expires in 30 days
        path="/auth/refresh"
    )

    return {"status": "success"}


@router.post("/login")
async def login(login_data: LoginRequest, db_session: SessionDep, response: Response) -> dict[str, str]:
    """Endpoint to authenticate (log in) a user and return an access token."""
    user = authenticate_user(db_session, login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expiry=15  # Token expires in 15 minutes
    )

    refresh_token = create_refresh_token(user.id, db_session)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=15 * 60,  # Cookie expires in 15 minutes
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # Cookie expires in 30 days
        path="/auth/refresh"
    )

    return {"status": "success"}


@router.post("/register_user")
async def register_user(user_data: UserCreate, db_session: SessionDep) -> UserOut:
    """Endpoint to register a new user. This is a placeholder and should be implemented with proper validation and error handling."""
    
    try:
        user = create_user(db_session, user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    return user


@router.post("/logout")
async def logout(request: Request, response: Response, db_session: SessionDep) -> dict[str, str]:
    """Endpoint to log out a user by clearing the authentication cookie."""
    decoded = decode_access_token(request.cookies.get("access_token", ""))
    if decoded:
        user_id = decoded.get("sub")
        if user_id:
            # Revoke all refresh tokens for this user
            revoke_all_refresh_tokens_for_user(int(user_id), db_session)

    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth/refresh")
    return {"status": "success"}


@router.get("/test_protected")
async def test_protected_route(token_payload: Annotated[dict, Depends(token_required)]) -> dict:
    """A protected endpoint that requires a valid access token to access."""
    return {"message": "You have accessed a protected route!", "user": token_payload.get("sub")}