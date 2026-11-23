from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.modules.ai import find_long_term_memories_by_user_id

user_router = APIRouter(prefix="/api/user")


@user_router.get("/profile")
async def profile(user_id: str = Query("", alias="userId")):
    """
    GET /api/user/profile?userId=...
    What we know about this traveler, for the Memory tab.
    """
    if not user_id:
        return JSONResponse({"error": "userId is required"}, status_code=400)
    try:
        return {"entries": await find_long_term_memories_by_user_id(user_id)}
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)
