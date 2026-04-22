from fastapi import APIRouter

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/")
async def get_progress():
    """Placeholder — will use SQLite in week 3."""
    return {"message": "Progress tracking coming in week 3"}
