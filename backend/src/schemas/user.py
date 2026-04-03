from pydantic import BaseModel, EmailStr

from src.schemas import BaseOutSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseOutSchema):
    id: int
    email: EmailStr
    username: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
