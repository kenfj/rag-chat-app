from unittest.mock import call

import pytest

from models import ChatRequest, Message
from models.stream_chat_request import StreamChatRequest
from services.llm_service import chat_completion, chat_stream


@pytest.mark.asyncio
async def test_chat_completion(
    mock_search_documents,
    mock_complete_response,
):
    req = ChatRequest(input="foo", history=[])

    result, history = await chat_completion(req)

    assert result == "Mocked complete_response"
    assert history == [
        Message(role="user", content="foo"),
        Message(role="assistant", content="Mocked complete_response"),
    ]

    assert mock_search_documents.call_count == 1
    assert mock_search_documents.call_args_list[0] == call("Mocked complete_response")

    assert mock_complete_response.call_count == 2


@pytest.mark.asyncio
async def test_chat_stream(
    mock_search_documents,
    mock_complete_response,
    mock_fastapi_request,
    mock_stream_response,
):
    req = StreamChatRequest(input="foo")

    content_generator = await chat_stream(mock_fastapi_request, req)

    result = "".join([res async for res in content_generator])

    assert result == (
        "Mocked stream_response 0Mocked stream_response 1Mocked stream_response 2"
    )

    assert mock_search_documents.call_count == 1
    assert mock_search_documents.call_args_list[0] == call("Mocked complete_response")

    assert mock_complete_response.call_count == 1
    assert mock_stream_response.call_count == 1

    assert mock_fastapi_request.state.session["history"] == [
        Message(role="user", content="foo"),
        # it will save_session after response in middleware
        # Message(role="assistant", content="Mocked complete_response"),
    ]
