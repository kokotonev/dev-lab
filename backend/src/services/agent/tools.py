import logging
from typing import Any

from src.schemas.meeting_scheduling import MeetingDetails

logger = logging.getLogger(__name__)

tools_schema = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event with attendees, and optional recurrence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string", "format": "email"}
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "frequency": {"enum": ["daily", "weekly", "monthly"]},
                        "count": {"type": "integer", "minimum": 1},
                    }
                }
            },
            "required": ["title", "start", "end"]
        }
    },
    {
        "name": "list_calendar_events",
        "description": "List all calendar events on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"}
            },
            "required": ["date"]
        }
    }
]

def run_tool(tool_name: str, tool_input: dict[str, Any]):
    if tool_name == "create_calendar_event":
        meeting_details = MeetingDetails.model_validate(tool_input)
        return create_calendar_event(meeting_details)
    elif tool_name == "list_calendar_events":
        date = tool_input.get("date")
        return list_calendar_events(date)
    else:
        logger.warning(f"Unknown tool: {tool_name}")
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def create_calendar_event(meeting_details: MeetingDetails):
    # Here you would implement the logic to create a calendar event using an API like Google Calendar or Microsoft Graph
    logger.info(f">>>>>>> Creating calendar event: {meeting_details}")
    return {"status": "created", "event_id": "evt_123"}


def list_calendar_events(date: str | None):
    # Here you would implement the logic to list calendar events for the given date using an API like Google Calendar or Microsoft Graph
    logger.info(f">>>>>>> Listing calendar events for date: {date}")
    return {"events": [{"title": "Blocker", "start": "09:00", "end": "10:00"}]}