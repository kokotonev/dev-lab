import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    revoked_at: datetime | None = None
