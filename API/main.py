from contextlib import asynccontextmanager

from typing import Annotated
from fastapi import FastAPI, Depends


from .database import create_db_and_tables, engine, Session
from .models import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return {"message": "Persona 5 Meta App API is running"}

