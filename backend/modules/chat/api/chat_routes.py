import asyncio
import json

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from backend.modules.ai import TurnEvent
from backend.modules.chat.domain.chat_service import clear_conversation, get_conversation, run_turn

chat_router = APIRouter(prefix="/api/chat")


class ChatRequest(BaseModel):
    userId: str | None = None
    sessionId: str | None = None
    message: str | None = None


@chat_router.post("")
async def chat(request: ChatRequest):
    """
    POST /api/chat { userId, sessionId, message }
    Runs one turn and streams what happens, one JSON event per line (see TurnEvent in ai/agent_workflow/stream_events.py).
    """

    if not request.userId or not request.sessionId or not request.message:
        return JSONResponse({"error": "userId, sessionId and message are required"}, status_code=400)

    async def events():
        queue: asyncio.Queue[TurnEvent | None] = asyncio.Queue()

        async def run() -> None:
            try:
                await run_turn(user_id=request.userId, session_id=request.sessionId, message=request.message, send=queue.put_nowait)
            except Exception as error:
                print(f"Turn failed: {error!r}")
                queue.put_nowait({"type": "error", "message": str(error)})
            finally:
                queue.put_nowait(None)

        task = asyncio.create_task(run())
        while (event := await queue.get()) is not None:
            yield json.dumps(event, default=str) + "\n"
        await task

    return StreamingResponse(events(), media_type="application/x-ndjson")


@chat_router.get("/session")
async def get_session(session_id: str = Query("", alias="sessionId")):
    """
    GET /api/chat/session?sessionId=...
    What the Memory tab shows about this conversation: how many messages and the summary.
    """

    if not session_id:
        return JSONResponse({"error": "sessionId is required"}, status_code=400)
    try:
        conversation = await get_conversation(session_id)
        return {"messageCount": len(conversation["messages"]), "summary": conversation["summary"]}
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@chat_router.delete("/session")
async def delete_session(session_id: str = Query("", alias="sessionId")):
    """DELETE /api/chat/session?sessionId=... : forget this conversation. What we know about the traveler stays."""

    if not session_id:
        return JSONResponse({"error": "sessionId is required"}, status_code=400)
    try:
        await clear_conversation(session_id)
        return {"ok": True}
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)
