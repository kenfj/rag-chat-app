from pydantic import BaseModel


class StreamChatRequest(BaseModel):
    input: str
