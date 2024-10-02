def generate_response_prompt(user_query, docs, history):
    history_txt = "\n".join(history)

    ai_prompt = (
        "As a luxury hotel concierge, based on the user's questions and the relevant information from the documents, "
        "please respond to the following inquiry with warmth and professionalism, and polished tone, "
        "highlighting key features and making recommendations also please use bullet points when possible. "
        "Please maintain an air of elegance and attentiveness in your responses. "
        "If user's question is not clear, please ask for clarification. "
        "If you think the user's question is not related to the hotel database, "
        "please answer you are not able to provide a relevant answer. "
        "If the latest user input is greeting, please greet back and ask how you can help briefly under 30 words.”."
    )

    info = "\n".join(
        [
            (
                f"Name: {doc['HotelName']}; "
                f"Description: {doc['Description']}; "
                f"Category: {doc['Category']}; "
                f"Tags: {doc['Tags']}; "
                f"ParkingIncluded: {doc['ParkingIncluded']}; "
                f"LastRenovationDate: {doc['LastRenovationDate']}; "
                f"Rating: {doc['Rating']}"
            )
            for doc in docs
        ]
    )

    return f"""
{ai_prompt}

Conversation history:
{history_txt or "No history yet"}

Here are some documents that match user's query:
{info or "Document not found"}

User: {user_query}
Ai:
"""
