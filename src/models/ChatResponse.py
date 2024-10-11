from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    messages: list[dict[str, str]]
