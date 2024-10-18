from pydantic import BaseModel

from models import Message


class ChatRequest(BaseModel):
    input: str
    history: list[Message]
