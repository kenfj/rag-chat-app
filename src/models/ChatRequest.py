from pydantic import BaseModel


class ChatRequest(BaseModel):
    input: str
    session_id: str
