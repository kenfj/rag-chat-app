import json

import chainlit as cl
import httpx

from utils.logger_setup import setup_logger

logger = setup_logger(__name__)


@cl.on_chat_start
async def main():
    await cl.Message(content="Welcome to Hotel Search RAG Chat Stream!").send()


# async POST https://www.python-httpx.org/async/
# update Message https://docs.chainlit.io/api-reference/message#update-a-message
@cl.on_message
async def chainlit_chat(message: cl.Message):
    session_id = cl.user_session.get("session_id", "")

    stream_url = "http://127.0.0.1:8000/chat-stream"
    headers = {"Content-Type": "application/json"}
    payload = {"input": message.content, "session_id": session_id}

    logger.info(f"Sending message to {stream_url}: {payload}")

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", stream_url, headers=headers, json=payload
        ) as response:
            msg = cl.Message(content="")
            await msg.send()

            buffer = ""
            is_first_element = True

            async for chunk in response.aiter_bytes():
                if is_first_element:
                    is_first_element = False

                    session_id = find_session_id(chunk)
                    cl.user_session.set("session_id", session_id)
                    continue

                buffer += chunk.decode("utf-8")
                msg.content = buffer
                await msg.update()


def find_session_id(chunk):
    first_element = chunk.decode("utf-8").strip()
    data = json.loads(first_element)
    session_id = data.get("session_id", "")

    return session_id
