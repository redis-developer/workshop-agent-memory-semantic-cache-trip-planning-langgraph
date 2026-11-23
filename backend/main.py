from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from backend.modules.ai import start_agent
from backend.modules.chat.api.chat_routes import chat_router
from backend.modules.user.api.user_routes import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_agent()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(chat_router)
app.include_router(user_router)
# The page. The API routes are checked first, and the files in frontend/ only when no route matched.
app.frontend("/", directory=Path(__file__).parent.parent / "frontend")
