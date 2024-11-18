import pytest

from repositories import search_documents


@pytest.mark.skip(reason="for local testing only")
def test_search_documents():
    response = search_documents("hotel")

    response_list = [x["HotelName"] for x in response]

    assert response_list == [
        "Triple Landscape Hotel",
        "Sublime Cliff Hotel",
        "Twin Dome Motel",
        "Secret Point Motel",
    ]
