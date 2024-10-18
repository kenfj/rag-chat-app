import chainlit as cl
import httpx

from config.logging_config import get_logger

logger = get_logger(__name__)


@cl.on_chat_start
async def main():
    await cl.Message(content="Welcome to Hotel Search RAG Chat Stream!").send()


# async POST https://www.python-httpx.org/async/
# update Message https://docs.chainlit.io/api-reference/message#update-a-message
@cl.on_message
async def chainlit_chat(message: cl.Message):
    session_id = cl.user_session.get("session_id", "")
    logger.info(f"session_id: {session_id}")

    stream_url = "http://127.0.0.1:8000/chat-stream"
    headers = {"Content-Type": "application/json"}
    payload = {"input": message.content}

    logger.info(f"Sending message to {stream_url}: {payload}")

    async with httpx.AsyncClient() as client:
        cookies = httpx.Cookies()
        cookies.set("session_id", session_id)

        async with client.stream(
            "POST", stream_url, headers=headers, cookies=cookies, json=payload
        ) as response:
            msg = cl.Message(content="")
            await msg.send()

            session_id = response.cookies.get("session_id")
            cl.user_session.set("session_id", session_id)

            buffer = ""

            async for chunk in response.aiter_bytes():
                buffer += chunk.decode("utf-8")
                msg.content = buffer
                await msg.update()


@cl.on_chat_end
def on_chat_end():
    logger.info("The user disconnected!")
    cl.user_session.set("session_id", None)
