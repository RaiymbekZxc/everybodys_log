from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers.authentication import router_auth
from .routers.health import router_health
from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(prefix="/api", router=router_health)
app.include_router(prefix="/api", router=router_auth)