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

        session = self.load_session(session_id)
        logger.info(f"session data: {session}")

        if "history" not in session:
            session["history"] = []

        request.state.session = session

        response: Response = await call_next(request)

        self.save_session(session_id, request.state.session)

        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    def find_session_id(self, request: Request):
        # optional GET param to get chat history for debugging
        session_id = request.query_params.get("session_id")

        if session_id is not None:
            return session_id

        # find session_id from cookie or create new session_id
        session_id = request.cookies.get("session_id")

        if session_id is None or session_id not in session_store:
            session_id = str(uuid.uuid4())
            session_store[session_id] = {}

        return session_id

    def load_session(self, session_id: str):
        return session_store.get(session_id, {})

    def save_session(self, session_id: str, session_data: dict):
        session_store[session_id] = session_data
