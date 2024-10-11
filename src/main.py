import uuid
from typing import Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from litellm import acompletion, completion

from config.env_config import (LLM_API_BASE, LLM_MODEL_NAME, SEARCH_API_KEY,
                               SEARCH_ENDPOINT)
from config.logging_config import get_logger
from models.ChatRequest import ChatRequest
from models.ChatResponse import ChatResponse
from models.StreamChatRequest import StreamChatRequest
from templates.system_prompt import system_chat_message, system_keyword_message

logger = get_logger(__name__)

index_name = "hotels-quickstart"
credential = AzureKeyCredential(SEARCH_API_KEY)
search_client = SearchClient(SEARCH_ENDPOINT, index_name, credential)


def search_documents(query: str):
    docs = search_client.search(search_text=query)
    return docs


def generate_response(messages: List[dict]):
    response = completion(
        model=LLM_MODEL_NAME,
        messages=messages,
        api_base=LLM_API_BASE,
    )
    return response


# https://docs.litellm.ai/docs/completion/stream#async-streaming
async def stream_response(messages: List[dict], session_id: str):
    response = await acompletion(
        model=LLM_MODEL_NAME,
        messages=messages,
        api_base=LLM_API_BASE,
        stream=True,
    )

    buffer = ""

    yield f'{{"session_id": "{session_id}"}}\n'

    async for chunk in response:
        content = chunk.choices[0].delta.content

        # the last element of chunk content is always None
        if content is not None:
            buffer += content
            yield content
        else:
            # Save to conversation history
            conversations[session_id].append({"role": "assistant", "content": buffer})


# ----- Web API -----

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

mount_chainlit(app=app, target="src/my_cl_app.py", path="/chainlit")

# In-memory storage for conversations
conversations: Dict[str, List[str]] = {}


@app.post("/chat")
def chat_response(req: ChatRequest) -> ChatResponse:
    messages = req.messages.copy()

    messages.insert(0, system_keyword_message)
    messages.append({"role": "user", "content": req.input})
    messages.append({"role": "assistant", "content": ""})

    keywords_response = generate_response(messages)
    keywords = keywords_response.choices[0].message.content

    logger.info(f"Search keywords: {keywords}")

    docs = search_documents(keywords)

    docs_text = "Documents:\n" + "\n".join([str(doc) for doc in docs])
    logger.info(docs_text)

    messages = req.messages.copy()

    messages.insert(0, system_chat_message(docs_text))
    messages.append({"role": "user", "content": req.input})
    messages.append({"role": "assistant", "content": ""})

    response = generate_response(messages)
    content = response.choices[0].message.content

    req.messages.append({"role": "assistant", "content": content})
    return {"response": content, "messages": req.messages}


@app.post("/chat-stream")
async def chat_stream(req: StreamChatRequest):
    if not req.session_id or req.session_id not in conversations:
        session_id = str(uuid.uuid4())
        req.session_id = session_id
        conversations[session_id] = []

    logger.info(f"Session ID: {req.session_id}")

    messages = conversations.get(req.session_id, []).copy()

    messages.insert(0, system_keyword_message)
    messages.append({"role": "user", "content": req.input})
    messages.append({"role": "assistant", "content": ""})

    logger.info(f"Messages: {messages}")

    keywords_response = generate_response(messages)
    keywords = keywords_response.choices[0].message.content

    logger.info(f"Search keywords: {keywords}")

    docs = search_documents(keywords) if "NONE" not in keywords else []

    docs_text = "Documents:\n" + "\n".join([str(doc) for doc in docs])
    logger.info(docs_text)

    messages = conversations.get(req.session_id, []).copy()

    messages.insert(0, system_chat_message(docs_text))
    messages.append({"role": "user", "content": req.input})
    messages.append({"role": "assistant", "content": ""})

    # Save to conversation history
    conversations[req.session_id].append({"role": "user", "content": req.input})

    content = stream_response(messages, req.session_id)
    return StreamingResponse(content, media_type="text/plain")


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"history": conversations.get(session_id, [])}
