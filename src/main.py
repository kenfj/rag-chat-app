import uuid
from typing import Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from litellm import acompletion, completion

from models.ChatRequest import ChatRequest
from models.Request import Request
from templates.keywords_prompt import generate_keywords_prompt
from templates.response_prompt import generate_response_prompt
from utils import settings
from utils.logger_setup import setup_logger

logger = setup_logger(__name__)

index_name = "hotels-quickstart"
credential = AzureKeyCredential(settings.SEARCH_API_KEY)
search_client = SearchClient(settings.SEARCH_ENDPOINT, index_name, credential)


def search_documents(query: str):
    docs = search_client.search(search_text=query)
    return docs


def generate_response(prompt):
    response = completion(
        model=settings.LLM_MODEL_NAME,
        messages=[{"content": prompt, "role": "user"}],
        api_base=settings.LLM_API_BASE,
    )
    return response


# https://docs.litellm.ai/docs/completion/stream#async-streaming
async def stream_response(prompt: str, session_id: str):
    response = await acompletion(
        model=settings.LLM_MODEL_NAME,
        messages=[{"content": prompt, "role": "user"}],
        api_base=settings.LLM_API_BASE,
        stream=True,
    )

    ai_response = "Ai: "

    yield f"{{\"session_id\": \"{session_id}\"}}\n"

    async for chunk in response:
        content = chunk.choices[0].delta.content

        # the last element of chunk content is always None
        if content is not None:
            ai_response += content
            yield content
        else:
            # Save to conversation history
            conversations[session_id].append(ai_response)


# ----- Web API -----

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

mount_chainlit(app=app, target="src/my_cl_app.py", path="/chainlit")

# In-memory storage for conversations
conversations: Dict[str, List[str]] = {}


@app.post("/chat")
def chat_response(req: Request):
    keywords_prompt = generate_keywords_prompt(req.input, req.history)

    keywords_response = generate_response(keywords_prompt)
    keywords = keywords_response.choices[0].message.content

    docs = search_documents(keywords)
    docs_list = [doc for doc in docs]

    logger.info(f"Documents:\n{"\n".join([str(doc) for doc in docs_list])}")

    response_prompt = generate_response_prompt(req.input, docs_list, req.history)

    ai_response = generate_response(response_prompt)
    ai_message = ai_response.choices[0].message.content

    req.history.append(f"AI: {ai_message}")
    return {"response": ai_message, "history": req.history}


@app.post("/chat-stream")
async def chat_stream(req: ChatRequest):
    if not req.session_id or req.session_id not in conversations:
        session_id = str(uuid.uuid4())
        req.session_id = session_id
        conversations[session_id] = []

    logger.info(f"Session ID: {req.session_id}")
    history = conversations.get(req.session_id, [])

    keywords_prompt = generate_keywords_prompt(req.input, history)

    keywords_response = generate_response(keywords_prompt)
    keywords = keywords_response.choices[0].message.content

    logger.info(f"Search keywords: {keywords}")

    if "NONE" in keywords:
        docs_list = []
    else:
        docs = search_documents(keywords)
        docs_list = [doc for doc in docs]

    logger.info(f"Documents:\n{"\n".join([str(doc) for doc in docs_list])}")

    response_prompt = generate_response_prompt(req.input, docs_list, history)

    # Save to conversation history
    conversations[req.session_id].append(f"User: {req.input}")

    content = stream_response(response_prompt, req.session_id)
    return StreamingResponse(content, media_type='text/plain')


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"history": conversations.get(session_id, [])}
