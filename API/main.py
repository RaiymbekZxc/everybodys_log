from contextlib import asynccontextmanager

from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlmodel import select

from .database import create_db_and_tables, SessionDep
from .models import UserInDB
from .auth import get_current_user, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return {"message": "Persona 5 Meta App API is running"}

@app.get('/users/me')
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)]):
    return current_user

@app.post('/token')
async def post_user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    statement = select(UserInDB).where(UserInDB.username == form_data.username)
    user = session.exec(statement=statement).first()
    
    iuop_exception = HTTPException(status_code=400, detail="Incorrect username or password.")

    if not user:
        raise iuop_exception    
    if not verify_password(form_data.password, user.hashed_password):
        raise iuop_exception
    
    return {"access_token": "placeholder", "token_type": "bearer"}
    