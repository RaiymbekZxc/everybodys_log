
from fastapi import APIRouter

from ..database import SessionDep

router_health = APIRouter(prefix="/health")

@router_health.get("/")
async def health():
    return {"status": "ok"}

@router_health.get("/database")
async def database(session: SessionDep):
    try:
        from sqlmodel import select
        session.exec(select(1))
        db_status = "ok"
    except Exception: 
        db_status = "unavailable"

    return {"database": db_status}