
from fastapi import APIRouter

from ..timpestampupdater import reset_period

router = APIRouter(prefix="/debug", include_in_schema=False)

@router.post("/reset")
def debug_reset():
    reset_period()
    return {"detail": "reset done"}

