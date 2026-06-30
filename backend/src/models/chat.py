from sqlalchemy import Text
from sqlmodel import SQLModel, Field

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"  # type: ignore[assignment]

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str = Field(max_length=255)

class Message(SQLModel, table=True):
    __tablename__ = "messages"  # type: ignore[assignment]

    id: int = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field(max_length=50)  # user/assistant/agent
    content: str = Field(sa_type=Text)