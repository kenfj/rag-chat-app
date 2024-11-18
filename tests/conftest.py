from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.search.documents import SearchItemPaged
from fastapi import Request
from fastapi.testclient import TestClient
from litellm.types.utils import Choices, Delta, ModelResponse, StreamingChoices

from models import Message

from .mock_data import fake_docs


@pytest.fixture()
def client():
    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def mock_fastapi_request():
    mock_req = MagicMock(spec=Request)
    mock_req.state.session = {"history": []}

    return mock_req


@pytest.fixture()
def mock_complete_response():
    mock_response = AsyncMock(spec=ModelResponse)
    mock_response.choices = [Choices(message={"content": "Mocked complete_response"})]

    with patch("services.llm_service.complete_response") as mock_func:
        mock_func.return_value = mock_response
        yield mock_func


@pytest.fixture()
def mock_stream_response():
    async def mock_response(messages: list[Message]):
        for i in range(3):
            yield ModelResponse(
                choices=[StreamingChoices(delta=Delta(f"Mocked stream_response {i}"))]
            )

    with patch("services.llm_service.stream_response") as mock_func:
        mock_func.side_effect = mock_response
        yield mock_func


@pytest.fixture()
def mock_search_documents():
    mock_response = MagicMock(spec=SearchItemPaged)
    mock_response.__iter__.return_value = iter(fake_docs)

    with patch("services.llm_service.search_documents") as mock_func:
        mock_func.return_value = mock_response
        yield mock_func
