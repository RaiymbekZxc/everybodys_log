
from typing import Annotated 
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv

import os

from jwt import PyJWTError, encode, decode
from jwt.exceptions import InvalidTokenError 

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pwdlib import PasswordHash
from sqlmodel import select

from .database import SessionDep
from .models import User, UserInDB, Token, TokenData

load_dotenv()

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

SECRET_KEY = os.getenv("SECRET_KEY", DUMMY_HASH)
ALGORITHM = os.getenv("ALGORITHM", "HS256") 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(session: SessionDep, id: int):
    user = session.get(UserInDB, id)
    return user

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def authenticate_user(session: SessionDep, username: str, password: str):
    user = session.get(UserInDB, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Couldn't authenticate the user.",
        headers={"WWW-Authenticate": "Bearer"})
    try: 
        payload = decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    statement = select(UserInDB).where(UserInDB.username == username)
    user = session.exec(statement=statement).first()
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expiration = datetime.now(timezone.utc) + expires_delta
    else: 
        expiration = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expiration})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
