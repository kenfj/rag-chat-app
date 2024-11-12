from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from config.settings import settings

index_name = settings.SEARCH_INDEX_NAME
credential = AzureKeyCredential(settings.SEARCH_API_KEY)
search_client = SearchClient(settings.SEARCH_ENDPOINT, index_name, credential)


def search_documents(query: str):
    docs = search_client.search(search_text=query)
    return docs
