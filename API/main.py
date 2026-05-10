from contextlib import asynccontextmanager

from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlmodel import select
from datetime import timedelta

from .database import create_db_and_tables, SessionDep
from .models import UserInDB, UserCreate
from .auth import get_current_user, verify_password, get_user, get_password_hash, create_user_in_db, create_access_token


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
    access_token = create_access_token(data={"sub": user.model_dump(exclude={"hashed_password"})}, expires_delta=timedelta(days=30))
    return {"access_token": access_token, "token_type": "bearer"}
    

@app.post('/register', status_code=201)
async def register_user(user_data: UserCreate, session: SessionDep):
    if await get_user(session=session, username=user_data.username):
        raise HTTPException(status_code=409, detail="Given username is already taken.")
    
    if await get_user(session=session, email=user_data.email):
        raise HTTPException(status_code=409, detail="Given email is already in use.")
    
    user = UserInDB(**user_data.model_dump(exclude={"password"}), hashed_password=get_password_hash(user_data.password))
    create_user_in_db(session=session, user=user)

    return {"detail": "user created."}