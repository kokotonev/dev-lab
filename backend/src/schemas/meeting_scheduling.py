from pydantic import BaseModel

class Recurrence(BaseModel):
    frequency: str  # "daily", "weekly", or "monthly"
    count: int     # number of occurrences

class MeetingDetails(BaseModel):
    title: str
    start: str
    end: str
    attendees: list[str]
    recurrence: Recurrence | None = None