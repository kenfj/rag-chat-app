# クイック スタート: REST を使用したキーワード検索
# https://learn.microsoft.com/ja-jp/azure/search/search-get-started-rest

# Getting started
# https://pypi.org/project/azure-search-documents/

# Azure AI Search REST API リファレンス
# https://learn.microsoft.com/ja-jp/rest/api/searchservice/

# 【Azure AI Search】フルテキスト検索のクイックスタートをやってみる
# https://qiita.com/nyarita/items/39ea015dbf1b51a4f8d9

# Azure SDK を使って Python から Azure AI Searchのインデックスを作成する
# https://zenn.dev/headwaters/articles/a806bdc8e1549c

# Azure SDK を使って Python から Azure AI Search のインデックスにjsonファイルのドキュメントを追加する
# https://zenn.dev/headwaters/articles/4ee7abdcc8cc54

# NOTE: required environment variable
# export REQUESTS_CA_BUNDLE=~/.aspnet/https/certificate.pem

# %%
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    CorsOptions,
    ScoringProfile,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SearchSuggester,
    SimpleField,
)

# %% [markdown]
# ### Create a SearchClient

endpoint = "https://localhost:5081/"
index_name = "hotels-quickstart"
search_api_key = "PUT-YOUR-SEARCH-SERVICE-ADMIN-API-KEY-HERE"
credential = AzureKeyCredential(search_api_key)

search_client = SearchClient(endpoint, index_name, credential)
index_client = SearchIndexClient(endpoint, credential)


# %% [markdown]
# ### Create Index

fields = [
    SimpleField(name="HotelId", type=SearchFieldDataType.String, key=True),
    SearchableField(name="HotelName", type=SearchFieldDataType.String, sortable=True),
    SearchableField(
        name="Description", type=SearchFieldDataType.String, analyzer_name="en.lucene"
    ),
    SearchableField(
        name="Description_fr",
        type=SearchFieldDataType.String,
        analyzer_name="fr.lucene",
    ),
    SearchableField(
        name="Category",
        type=SearchFieldDataType.String,
        facetable=True,
        filterable=True,
        sortable=True,
    ),
    SearchableField(
        name="Tags",
        type=SearchFieldDataType.String,
        facetable=True,
        filterable=True,
    ),
    SimpleField(
        name="ParkingIncluded",
        type=SearchFieldDataType.Boolean,
        facetable=True,
        filterable=True,
        sortable=True,
    ),
    SimpleField(
        name="LastRenovationDate",
        type=SearchFieldDataType.DateTimeOffset,
        facetable=True,
        filterable=True,
        sortable=True,
    ),
    SimpleField(
        name="Rating",
        type=SearchFieldDataType.Double,
        facetable=True,
        filterable=True,
        sortable=True,
    ),
]

scoring_profiles: list[ScoringProfile] = []
suggesters: list[SearchSuggester] = [
    SearchSuggester(
        name="sg", source_fields=["Tags", "Address/City", "Address/Country"]
    )
]
cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

index = SearchIndex(
    name=index_name,
    fields=fields,
    suggesters=suggesters,
    scoring_profiles=scoring_profiles,
    cors_options=cors_options,
)

index_result = index_client.create_index(index)  # .create_or_update_index(index)
print(f" {index_result.name} created")


# %% [markdown]
# ### Adding Documents

documents = [
    {
        "@search.action": "upload",
        "HotelId": "1",
        "HotelName": "Secret Point Motel",
        "Description": "The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city, as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
        "Description_fr": "L'hôtel est idéalement situé sur la principale artère commerciale de la ville en plein cœur de New York. A quelques minutes se trouve la place du temps et le centre historique de la ville, ainsi que d'autres lieux d'intérêt qui font de New York l'une des villes les plus attractives et cosmopolites de l'Amérique.",
        "Category": "Boutique",
        "Tags": "pool, air conditioning, concierge",
        "ParkingIncluded": False,
        "LastRenovationDate": "1970-01-18T00:00:00Z",
        "Rating": 3.60,
    },
    {
        "@search.action": "upload",
        "HotelId": "2",
        "HotelName": "Twin Dome Motel",
        "Description": "The hotel is situated in a  nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and first-class hotel in which art and unique historical elements coexist with the most modern comforts.",
        "Description_fr": "L'hôtel est situé dans une place du XIXe siècle, qui a été agrandie et rénovée aux plus hautes normes architecturales pour créer un hôtel moderne, fonctionnel et de première classe dans lequel l'art et les éléments historiques uniques coexistent avec le confort le plus moderne.",
        "Category": "Boutique",
        "Tags": "pool, free wifi, concierge",
        "ParkingIncluded": False,
        "LastRenovationDate": "1979-02-18T00:00:00Z",
        "Rating": 3.60,
    },
    {
        "@search.action": "upload",
        "HotelId": "3",
        "HotelName": "Triple Landscape Hotel",
        "Description": "The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.",
        "Description_fr": "L'hôtel est situé dans une place du XIXe siècle, qui a été agrandie et rénovée aux plus hautes normes architecturales pour créer un hôtel moderne, fonctionnel et de première classe dans lequel l'art et les éléments historiques uniques coexistent avec le confort le plus moderne.",
        "Category": "Resort and Spa",
        "Tags": "air conditioning, bar, continental breakfast",
        "ParkingIncluded": True,
        "LastRenovationDate": "2015-09-20T00:00:00Z",
        "Rating": 4.80,
    },
    {
        "@search.action": "upload",
        "HotelId": "4",
        "HotelName": "Sublime Cliff Hotel",
        "Description": "Sublime Cliff Hotel is located in the heart of the historic center of Sublime in an extremely vibrant and lively area within short walking distance to the sites and landmarks of the city and is surrounded by the extraordinary beauty of churches, buildings, shops and monuments. Sublime Cliff is part of a lovingly restored 1800 palace.",
        "Description_fr": "Le sublime Cliff Hotel est situé au coeur du centre historique de sublime dans un quartier extrêmement animé et vivant, à courte distance de marche des sites et monuments de la ville et est entouré par l'extraordinaire beauté des églises, des bâtiments, des commerces et Monuments. Sublime Cliff fait partie d'un Palace 1800 restauré avec amour.",
        "Category": "Boutique",
        "Tags": "concierge, view, 24-hour front desk service",
        "ParkingIncluded": True,
        "LastRenovationDate": "1960-02-06T00:00:00Z",
        "Rating": 4.60,
    },
]

try:
    upload_result = search_client.upload_documents(documents=documents)
    print("Upload of new document succeeded: {}".format(upload_result[0].succeeded))

    print(upload_result[0].error_message, flush=True)

except Exception as ex:
    print(str(ex), flush=True)


# %% [markdown]
# ### Do Search

results = search_client.search(search_text="heart")

for result in results:
    print("{}: {}".format(result["HotelId"], result["HotelName"]), flush=True)


# %% [markdown]
# ### Do Search 2nd

results = search_client.search(
    query_type="simple",
    search_text="hotel",
    select=["HotelName", "Description"],
    include_total_count=True,
)

print("Total Documents Matching Query:", results.get_count())

for result in results:
    print("{}: {}".format(result["@search.score"], result["HotelName"]), flush=True)


# %%
