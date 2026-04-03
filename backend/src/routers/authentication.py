from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from src.schemas.common import Tags
from src.schemas.user import UserCreate, UserOut, LoginRequest
from src.services.auth import create_access_token, token_required
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
    return {"email": token_payload.get("sub")}


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
        data={"sub": user.email},
        expiry=60  # Token expires in 60 minutes
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60,  # Cookie expires in 1 hour
        path="/"
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
async def logout(response: Response) -> dict[str, str]:
    """Endpoint to log out a user by clearing the authentication cookie."""
    response.delete_cookie(key="access_token", path="/")
    return {"status": "success"}


@router.get("/test_protected")
async def test_protected_route(token_payload: Annotated[dict, Depends(token_required)]) -> dict:
    """A protected endpoint that requires a valid access token to access."""
    return {"message": "You have accessed a protected route!", "user": token_payload.get("sub")}