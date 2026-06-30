"""
Service functions related to agent interaction, including response handling and response data processing.
"""
import logging
import anthropic

from anthropic.types.message import Message
from sqlmodel import Session, select, col, delete
from collections.abc import Sequence

from src.models.chat import Conversation, Message as ChatMessage

logger = logging.getLogger(__name__)

anthropic_client = anthropic.Anthropic()

def extract_text(response: Message) -> str | None:
    """Return the first text block from a response, if any."""
    for block in response.content:
        if block.type == "text":
            return block.text
    return None


def handle_response(response: Message) -> str | None:
    """Handle different stop_reasons and return the response text when one is available."""
    if response.stop_reason == "end_turn":
        return extract_text(response)
    elif response.stop_reason == "max_tokens":
        # Partial answer: still surface whatever text was generated before the cutoff.
        logger.info("Response stopped due to max tokens limit.")
        return extract_text(response)
    elif response.stop_reason == "tool_use":
        logger.info("Tool use detected in response.")
    elif response.stop_reason == "model_context_window_exceeded":
        logger.info("Response stopped due to model context window exceeded.")
    elif response.stop_reason == "pause_turn":
        logger.info("Response stopped due to pause turn.")
    elif response.stop_reason == "stop_sequence":
        logger.info("Response stopped due to stop sequence.")
    elif response.stop_reason == "refusal":
        logger.info("Response stopped due to refusal.")
    else:
        logger.info(f"Response stopped due to {response.stop_reason}")
        return extract_text(response)
    return None


def get_user_conversation(user_id: int, db_session: Session) -> Sequence[ChatMessage]:
    """Retrieve the conversation history for a given user."""
    
    conversation = db_session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    conversation_history = db_session.exec(
        select(ChatMessage).where(ChatMessage.conversation_id == conversation.id).order_by(col(ChatMessage.id))
    ).all() if conversation else []

    return conversation_history

def send_user_message(user_id: int, message_content: str, db_session: Session) -> str | None:
    """Send a user's message to the agent and get a response."""
    store_user_message(user_id, message_content, db_session)

    conversation = get_user_conversation(user_id, db_session)

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a helpful assistant that provides concise answers to user questions.",
        messages=[{"role": msg.role, "content": msg.content} for msg in conversation],  # type: ignore
    )

    parsed_response = handle_response(response)

    if parsed_response:
        store_model_response(user_id, parsed_response, db_session)
        return parsed_response


def store_user_message(user_id: int, message_content: str, db_session: Session) -> None:
    """Store a user's message in the database."""
    
    conversation = db_session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id, title="User Conversation")  # Placeholder title; will be extended when multiple conversations are supported
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)

    user_message = ChatMessage(
        conversation_id=conversation.id,
        role="user",
        content=message_content
    )
    db_session.add(user_message)
    db_session.commit()


def store_model_response(user_id: int, response_content: str, db_session: Session) -> None:
    """Store the model's response in the database."""
    
    conversation = db_session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        logger.error(f"No conversation found for user {user_id} when trying to store model response.")
        return

    model_message = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=response_content
    )
    db_session.add(model_message)
    db_session.commit()


def clear_user_conversation(user_id: int, db_session: Session) -> None:
    """Clear the conversation history for a given user."""
    
    conversation = db_session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if conversation:
        db_session.exec(
            delete(ChatMessage).where(col(ChatMessage.conversation_id) == conversation.id)
        )
        db_session.commit()