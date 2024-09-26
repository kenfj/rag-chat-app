from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from litellm import completion

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
    logger.info(f"Searching documents query: {query}")

    docs = search_client.search(search_text=query)
    return docs


def generate_response(prompt):
    response = completion(
        model=settings.LLM_MODEL_NAME,
        messages=[{"content": prompt, "role": "user"}],
        api_base=settings.LLM_API_BASE,
    )
    return response


# ----- Web API -----

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


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
