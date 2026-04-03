from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str | None = Field(default=None, unique=True, index=True)


class UserCredential(SQLModel, table=True):
    __tablename__ = "user_credentials"  # type: ignore[assignment]

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    provider: str = Field(index=True)  # "local", "google", "github", etc.
    provider_user_id: str | None = Field(default=None)  # NULL for local, OAuth sub/id for others
    password_hash: str | None = Field(default=None, exclude=True)  # Only set for provider="local"
