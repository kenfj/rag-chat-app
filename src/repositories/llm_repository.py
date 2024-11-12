from typing import AsyncGenerator

from litellm import acompletion
from litellm.types.utils import ModelResponse
from litellm.utils import CustomStreamWrapper

from config.settings import settings
from models import Message


async def complete_response(messages: list[Message]):
    response = await acompletion(
        model=settings.model,
        messages=messages,
        api_base=settings.api_base,
        stream=False,
    )

    if not isinstance(response, ModelResponse):
        raise ValueError(f"Unexpected type: {type(response)} for ModelResponse")

    return response


# https://docs.litellm.ai/docs/completion/stream#async-streaming
async def stream_response(messages: list[Message]):
    response = await acompletion(
        model=settings.model,
        messages=messages,
        api_base=settings.api_base,
        stream=True,
    )

    # AsyncGenerator for non-stream and CustomStreamWrapper for stream
    if not isinstance(response, AsyncGenerator | CustomStreamWrapper):
        raise ValueError(f"Unexpected type: {type(response)} for CustomStreamWrapper")

    return response
