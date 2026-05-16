from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routers import health, authentication, admin
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


app.include_router(prefix="/api", router=health.router)
app.include_router(prefix="/api", router=authentication.router)
app.include_router(prefix="/api", router=admin.router)
app.include_router(prefix="/api", router=admin.router_secret)