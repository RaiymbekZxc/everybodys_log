
from fastapi import APIRouter

from ..database import SessionDep

router = APIRouter(prefix="/health")

@router.get("/")
async def health():
    return {"status": "ok"}

@router.get("/database")
async def database(session: SessionDep):
    try:
        from sqlmodel import select
        session.exec(select(1))
        db_status = "ok"
    except Exception: 
        db_status = "unavailable"

    return {"database": db_status}