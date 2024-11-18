import json
from unittest.mock import call

from fastapi.encoders import jsonable_encoder

from models import ChatRequest, Message, StreamChatRequest
from models.chat_response import ChatResponse
from templates.system_prompt import create_chat_messages, create_keyword_messages

from ..mock_data import fake_docs

# Integration tests for the chat router


def test_post_chat_completion(
    client,
    mock_search_documents,
    mock_complete_response,
):
    request = ChatRequest(input="foo", history=[])
    response = client.post("/chat", json=jsonable_encoder(request))

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    content = response.content.decode("utf-8")  # Decode bytes to string

    expected_response = ChatResponse(
        response="Mocked complete_response",
        history=[
            Message(role="user", content="foo"),
            Message(role="assistant", content="Mocked complete_response"),
        ],
    )
    expected = json.dumps(jsonable_encoder(expected_response), separators=(",", ":"))

    assert content == expected

    assert mock_search_documents.call_count == 1
    assert mock_search_documents.call_args_list[0] == call("Mocked complete_response")

    assert mock_complete_response.call_count == 2

    history = [Message(role="user", content="foo")]
    expected_search_messages = create_keyword_messages(history)

    assert mock_complete_response.call_args_list[0] == call(expected_search_messages)

    expected_chat_messages = create_chat_messages(history, iter(fake_docs))

    assert mock_complete_response.call_args_list[1] == call(expected_chat_messages)


def test_post_chat_stream(
    client,
    mock_search_documents,
    mock_complete_response,
    mock_stream_response,
):
    request = StreamChatRequest(input="foo")
    response = client.post("/chat-stream", json=jsonable_encoder(request))

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    content = response.content.decode("utf-8")  # Decode bytes to string

    expected = (
        "Mocked stream_response 0Mocked stream_response 1Mocked stream_response 2"
    )

    assert content == expected

    assert mock_search_documents.call_count == 1
    assert mock_search_documents.call_args_list[0] == call("Mocked complete_response")

    assert mock_complete_response.call_count == 1

    history = [Message(role="user", content="foo")]
    expected_search_messages = create_keyword_messages(history)

    assert mock_complete_response.call_args_list[0] == call(expected_search_messages)

    assert mock_stream_response.call_count == 1

    expected_chat_messages = create_chat_messages(history, iter(fake_docs))

    assert mock_stream_response.call_args_list[0] == call(expected_chat_messages)
