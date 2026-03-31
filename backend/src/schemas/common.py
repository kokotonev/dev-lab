
from enum import Enum
from pydantic import BaseModel

class Tags(str, Enum):
    """Tags for categorizing routes."""
    auth = "Authentication"

class Token(BaseModel):
    """Schema for required OAuth2 access token response."""
    access_token: str
    token_type: str