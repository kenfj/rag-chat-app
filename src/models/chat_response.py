from pydantic import BaseModel

from models import Message


class ChatResponse(BaseModel):
    response: str
    history: list[Message]
