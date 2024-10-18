import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging_config import get_logger

logger = get_logger(__name__)

# In-memory storage for session data.
# (key: session_id, value: session_data)
session_store: dict[str, dict] = {}


class StateSessionMiddleware(BaseHTTPMiddleware):
    """
    request.state.session dict for in-memory session store.
    request.session is managed by Starlette and readonly
    so use request.state.session instead.
    """

    async def dispatch(self, request: Request, call_next):
        session_id = self.find_session_id(request)
        logger.info("session_id: " + session_id)

        request.state.session = self.load_session(session_id)

        logger.warning(request.state.session)
        response: Response = await call_next(request)

        self.save_session(session_id, request.state.session)

        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    def find_session_id(self, request: Request):
        session_id = request.cookies.get("session_id")

        if session_id is None or session_id not in session_store:
            session_id = str(uuid.uuid4())
            session_store[session_id] = {}

        return session_id

    def load_session(self, session_id: str):
        return session_store.get(session_id, {})

    def save_session(self, session_id: str, session_data: dict):
        session_store[session_id] = session_data
