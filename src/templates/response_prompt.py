def generate_response_prompt(user_query, docs, history):
    history_txt = "\n".join(history)

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
Based on the user's previous questions and the relevant information from the documents,
please provide a concise and friendly answer summarizing the best options for the user,
highlighting key features and making recommendations.

If the latest user input is greeting, please greet back and ask how you can help.

User's Query: "{user_query}"

Here are some documents that match user's query:
{info or "Document not found"}

Here is the conversation history:
{history_txt}
"""
