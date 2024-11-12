from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from models import ChatRequest, ChatResponse, Message, StreamChatRequest
from services import chat_completion, chat_stream

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_response(req: ChatRequest):
    content, history = await chat_completion(req)
    return ChatResponse(response=content, history=history)


@router.post("/chat-stream")
async def chat_stream_response(request: Request, req: StreamChatRequest):
    content = await chat_stream(request, req)
    return StreamingResponse(content, media_type="text/plain")


@router.get("/chat-history", response_model=list[Message])
async def chat_history(request: Request):
    return request.state.session.get("history", [])
