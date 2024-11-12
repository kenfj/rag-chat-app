from typing import Iterator

from jinja2 import Template

from models import Message

# System Role Message: Setting Context and Guiding the Model

_system_keyword_prompt = (
    "Based on the user's question, "
    "please provide only the relevant keywords "
    "for a database search without additional explanations. "
    "If you think the user's question is not related to the hotel database, "
    "please answer just one word 'NONE'. "
    "If you think it is follow-up question of your previous answers, "
    "please provide the relevant keywords based on the previous conversations. "
    "The keywords should capture the main concepts and intent of the question. "
    "If database query is not necessary, please answer just one word 'NONE'."
)


def system_keyword_message():
    return Message(role="system", content=_system_keyword_prompt)


_system_chat_prompt = (
    "As a luxury hotel concierge, based on the user's questions and the relevant information from the documents, "
    "please respond to the following inquiry with warmth and professionalism, and polished tone, "
    "highlighting key features and making recommendations also please use bullet points when possible. "
    "Please maintain an air of elegance and attentiveness in your responses. "
    "If user's question is not clear, please ask for clarification. "
    "If you think the user's question is not related to the hotel database, "
    "please answer you are not able to provide a relevant answer. "
    "If the latest user input is greeting, please greet back and ask how you can help briefly under 30 words.”."
)


system_content_template = """\
{{ system_chat_prompt }}

Documents:
{% for doc in docs -%}
{{ doc }}
{% endfor %}
"""


def system_chat_message(docs: Iterator[dict]):
    template = Template(system_content_template)
    system_content = template.render(system_chat_prompt=_system_chat_prompt, docs=docs)

    return Message(role="system", content=system_content)


place_holder_message = Message(role="assistant", content="")


def create_keyword_messages(history: list[Message]):
    return [system_keyword_message()] + history + [place_holder_message]


def create_chat_messages(history: list[Message], docs: Iterator[dict]):
    return [system_chat_message(docs)] + history + [place_holder_message]
