from fastapi import APIRouter
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "message": "SciPaper API is running!"}
