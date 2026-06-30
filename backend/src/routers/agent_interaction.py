import anthropic
import logging
import json

from typing import Annotated, Any
from pydantic import BaseModel
from fastapi import APIRouter, Body, Depends

from src.schemas.common import Tags
from src.services.auth import token_required
from src.services.agent import (
    get_user_conversation, 
    clear_user_conversation,
    send_user_message,
)
from src.database import SessionDep

logger = logging.getLogger(__name__)

anthropic_client = anthropic.Anthropic()

router = APIRouter(
    prefix="/agent",
    tags=[Tags.agent],
)

teams_conversation_history = []
ask_conversation_history = []
scheduler_conversation_history = []

class TeamInfo(BaseModel):
    team_name: str
    most_popular_player: str
    number_of_championships: int

class Teams(BaseModel):
    teams: list[TeamInfo]


@router.get("/get_conversation")
async def get_conversation(token_payload: Annotated[dict, Depends(token_required)], db_session: SessionDep):
    """
    Retrieve the conversation history for the authenticated user.
    NOTE: For the moment, each user can have just one conversation, so we will return the messages from that conversation.
    """
    user_id = int(token_payload["sub"])
    user_conversation = get_user_conversation(user_id, db_session)
    return {"conversation_history": user_conversation}


@router.post("/ask")
async def ask(message: Annotated[str, Body(embed=True)], token_payload: Annotated[dict, Depends(token_required)], db_session: SessionDep):
    """
    Add a new user message to the conversation history for the authenticated user and get a response from the model.
    If the user has no existing conversation, a new one will be created.
    NOTE: For the moment, each user can have just one conversation, so we will not be adding title or other metadata to the conversation.
    """
    user_id = int(token_payload["sub"])

    response = send_user_message(user_id, message, db_session)

    return {"response": response}


@router.delete("/clear_conversation")
async def clear_conversation(token_payload: Annotated[dict, Depends(token_required)], db_session: SessionDep):
    """
    Clear the conversation history for the authenticated user.
    NOTE: For the moment, each user can have just one conversation, so we will clear the messages from that conversation.
    """
    user_id = int(token_payload["sub"])
    clear_user_conversation(user_id, db_session)
    return {"status": "success", "message": "Conversation history cleared."}
