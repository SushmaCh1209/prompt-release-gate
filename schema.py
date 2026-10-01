from typing import Literal
from pydantic import BaseModel


class NoteResult(BaseModel):
    summary: str
    sentiment: Literal["positive", "neutral", "negative"]
    next_action: str
    urgency: Literal["low", "medium", "high"]