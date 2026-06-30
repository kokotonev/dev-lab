import anthropic
import logging
import json

from typing import Annotated, Any
from pydantic import BaseModel
from fastapi import APIRouter, Body, Depends

from src.schemas.common import Tags
from src.services.auth import token_required
from src.services.agent.conversation import (
    get_user_conversation, 
    clear_user_conversation,
    send_user_message,
)
from src.services.agent.tools import tools_schema, run_tool
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


@router.post("/schedule_meeting")
async def schedule_meeting(message: Annotated[str, Body(embed=True)]):
    """
    Oversimplified example of tool usage with Claude. 
    The user message is sent to Claude, which may call a tool. The tool result is sent back to Claude, which produces a final answer.
    """
    scheduler_conversation_history = [{"role": "user", "content": message}]

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools_schema,  # type: ignore
        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        system="You are a helpful assistant that creates calendar events based on user input.",
        messages=scheduler_conversation_history,  # type: ignore
    )


    while response.stop_reason == "tool_use":
        # When Claude calls a tool, the response has stop_reason "tool_use"
        # and the content array contains a tool_use block alongside any text.
        logger.info(f"---> stop_reason: {response.stop_reason}")

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                logger.info(f"Tool use detected in response: {block.name}")
                tool_res = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_res),
                })

        scheduler_conversation_history.append({"role": "assistant", "content": response.content})  # type: ignore

        scheduler_conversation_history.append(
            { # type: ignore
                "role": "user",
                "content": tool_results,  # type: ignore
            }
        )

        # Send the result back. The tool_result block goes in a user message and
        # its tool_use_id must match the id from the tool_use block above. The
        # assistant's previous response is included so Claude has the full history.
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools_schema,  # type: ignore
            tool_choice={"type": "auto", "disable_parallel_tool_use": True},
            messages=scheduler_conversation_history,  # type: ignore

        )

    # With the tool result in hand, Claude produces a final natural-language
    # answer and stop_reason becomes "end_turn".
    logger.info(f"### stop_reason: {response.stop_reason}")
    final_text = next(block for block in response.content if block.type == "text")
    logger.info(f"### Final text: {final_text.text}")

    return {"final_response": final_text.text}