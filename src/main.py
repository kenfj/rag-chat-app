from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from chainlit.utils import mount_chainlit
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from litellm import acompletion, completion

from config.logging_config import get_logger
from config.settings import settings
from middleware import StateSessionMiddleware
from models import ChatRequest, ChatResponse, Message, StreamChatRequest
from templates.system_prompt import system_chat_message, system_keyword_message

logger = get_logger(__name__)

index_name = "hotels-quickstart"
credential = AzureKeyCredential(settings.SEARCH_API_KEY)
search_client = SearchClient(settings.SEARCH_ENDPOINT, index_name, credential)


def search_documents(query: str):
    docs = search_client.search(search_text=query)
    return docs


def generate_response(messages: list[Message]):
    response = completion(
        model=settings.model,
        messages=messages,
        api_base=settings.api_base,
    )
    return response


# https://docs.litellm.ai/docs/completion/stream#async-streaming
async def async_stream_response(messages: list[Message]):
    response = await acompletion(
        model=settings.model,
        messages=messages,
        api_base=settings.api_base,
        stream=True,
    )
    return response


async def stream_response(request: Request, messages: list[Message]):
    buffer = ""
    response = await async_stream_response(messages)

    if "history" not in request.state.session:
        request.state.session["history"] = []

    # the last element of chunk content is always None
    async for chunk in response:
        content = chunk.choices[0].delta.content

        if content is not None:
            buffer += content
            yield content
        else:
            # Save LLM message to chat history
            assistant_message = Message(role="assistant", content=buffer)
            request.state.session["history"].append(assistant_message)


# ----- Web API -----

app = FastAPI()

app.add_middleware(StateSessionMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

mount_chainlit(app=app, target="src/my_cl_app.py", path="/chainlit")


@app.post("/chat", response_model=ChatResponse)
def chat_response(req: ChatRequest):
    history = req.history.copy()

    # Save user input to chat history
    user_message = Message(role="user", content=req.input)
    history.append(user_message)

    messages = create_keyword_messages(history)

    keywords_response = generate_response(messages)
    keywords = keywords_response.choices[0].message.content

    logger.info(f"Search keywords: {keywords}")

    docs = search_documents(keywords) if "NONE" not in keywords else []

    docs_text = "Documents:\n" + "\n".join([str(doc) for doc in docs])
    logger.info(docs_text)

    messages = create_chat_messages(history, docs_text)

    response = generate_response(messages)
    content = response.choices[0].message.content

    # Save LLM output to chat history
    assistant_message = Message(role="assistant", content=content)
    history.append(assistant_message)

    return ChatResponse(response=content, history=history)


@app.post("/chat-stream")
async def chat_stream(request: Request, req: StreamChatRequest):
    if "history" not in request.state.session:
        request.state.session["history"] = []

    # Save user input to chat history
    request_message = Message(role="user", content=req.input)
    request.state.session["history"].append(request_message)

    messages = create_keyword_messages(request.state.session["history"])

    keywords_response = generate_response(messages)
    keywords = keywords_response.choices[0].message.content

    logger.info(f"Search keywords: {keywords}")

    docs = search_documents(keywords) if "NONE" not in keywords else []

    docs_text = "Documents:\n" + "\n".join([str(doc) for doc in docs])
    logger.info(docs_text)

    messages = create_chat_messages(request.state.session["history"], docs_text)

    content = stream_response(request, messages)

    return StreamingResponse(content, media_type="text/plain")


@app.get("/chat-history", response_model=list[Message])
async def chat_history(request: Request, session_id: str = Query(None)):
    """optionally pass session_id to get chat history for debugging"""
    if session_id is not None:
        middleware = StateSessionMiddleware(app)
        request.state.session = middleware.load_session(session_id)

    return request.state.session.get("history", [])


place_holder_message = Message(role="assistant", content="")


def create_keyword_messages(history: list[Message]):
    return [system_keyword_message] + history + [place_holder_message]


def create_chat_messages(history: list[Message], docs_text: str):
    return [system_chat_message(docs_text)] + history + [place_holder_message]
