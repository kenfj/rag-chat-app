from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.logging_config import get_logger
from config.settings import ENV
from middleware import StateSessionMiddleware
from routes import chat_router

logger = get_logger(__name__)

logger.info(f"ENV: {ENV}")


app = FastAPI()

app.add_middleware(StateSessionMiddleware)

app.include_router(chat_router.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

mount_chainlit(app=app, target="src/my_cl_app.py", path="/chainlit")
