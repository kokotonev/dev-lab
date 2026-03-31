from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str | None = Field(default=None, unique=True, index=True)
    hashed_password: str = Field(exclude=True)  # Exclude from Pydantic models by default