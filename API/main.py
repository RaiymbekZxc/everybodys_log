from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.authentication import router_auth
from .routers.health import router_health
from .routers.admin import router_admin
from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(prefix="/api", router=router_health)
app.include_router(prefix="/api", router=router_auth)
app.include_router(prefix="/api", router=router_admin)