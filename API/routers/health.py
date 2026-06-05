
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..database import SessionDep

router = APIRouter(prefix="/health", tags=["Production"])

@router.get("/")
async def health():
    return {"status": "ok"}

@router.get("/database")
async def database(session: SessionDep):
    try:
        from sqlmodel import select
        session.exec(select(1))
    except Exception: 
        raise HTTPException(500, detail="Database is not available.")

    return {"database": "ok"}