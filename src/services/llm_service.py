from typing import Iterator

from fastapi import Request
from litellm.types.utils import Choices, ModelResponse, StreamingChoices
from litellm.utils import CustomStreamWrapper

from config.logging_config import get_logger
from models import ChatRequest, Message, StreamChatRequest
from repositories import complete_response, search_documents, stream_response
from templates.system_prompt import create_chat_messages, create_keyword_messages
from utils.converters import to_pretty_json

logger = get_logger(__name__)


async def chat_completion(req: ChatRequest):
    history = req.history.copy()

    # Save user input to chat history
    user_message = Message(role="user", content=req.input)
    history.append(user_message)

    messages = create_keyword_messages(history)
    keywords_response = await complete_response(messages)
    keywords = create_complete_response(keywords_response)

    docs = find_docs(keywords)
    messages = create_chat_messages(history, docs)

    logger.info(f"Chat completion prompt: {to_pretty_json(messages)}")

    response = await complete_response(messages)
    content = create_complete_response(response) or "No response found"

    # Save LLM output to chat history
    assistant_message = Message(role="assistant", content=content)
    history.append(assistant_message)

    return content, history


async def chat_stream(request: Request, req: StreamChatRequest):
    history: list[Message] = request.state.session["history"]

    # Save user input to chat history
    user_message = Message(role="user", content=req.input)
    history.append(user_message)

    messages = create_keyword_messages(history)
    keywords_response = await complete_response(messages)
    keywords = create_complete_response(keywords_response)

    docs = find_docs(keywords)
    messages = create_chat_messages(history, docs)

    logger.info(f"Chat stream prompt: {to_pretty_json(messages)}")

    response = await stream_response(messages)
    content_generator = create_stream_response(request, response)

    return content_generator


def create_complete_response(response: ModelResponse):
    choice = response.choices[0]

    if not isinstance(choice, Choices):
        raise ValueError(f"Unexpected type: {type(choice)} for Choices")

    content = choice.message.content

    return content


async def create_stream_response(request: Request, response: CustomStreamWrapper):
    buffer = ""

    # the last element of chunk content is always None
    async for chunk in response:
        choice = chunk.choices[0]

        if not isinstance(choice, StreamingChoices):
            raise ValueError(f"Unexpected type: {type(choice)} for StreamingChoices")

        content = choice.delta.content

        if content is not None:
            buffer += content
            yield content
        else:
            # Save LLM message to chat history
            assistant_message = Message(role="assistant", content=buffer)
            request.state.session["history"].append(assistant_message)


def find_docs(keywords: str | None):
    logger.info(f"Search keywords: {keywords}")

    if keywords and "NONE" not in keywords:
        docs = search_documents(keywords)
    else:
        docs: Iterator[dict] = iter([])

    return docs
