
from typing import Annotated 
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv

import os

import jwt 
from jwt.exceptions import InvalidTokenError 

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash
from sqlmodel import select

from .database import SessionDep
from .models import tblUser

load_dotenv()

password_hash = PasswordHash.recommended()
blacklisted_tokens = set()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

DUMMY_HASH = password_hash.hash("dummypassword")
SECRET_KEY = os.getenv("SECRET_KEY", DUMMY_HASH)
ALGORITHM = os.getenv("ALGORITHM", "HS256") 

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(session: SessionDep, id: int | None = None, username: str | None = None, email: str | None = None) -> tblUser | None:
    if not username and not id and not email: 
        raise ValueError("Arguments must have ID, Username or Email.")
    if id: 
        return session.get(tblUser, id)
    if username:
        statement = session.exec(select(tblUser).where(tblUser.Username==username))
        return statement.first()
    if email:
        statement = session.exec(select(tblUser).where(tblUser.Email==email))
        return statement.first()

async def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user(session=session, username=username)
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
    
    if token in blacklisted_tokens:
        raise credentials_exception

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(session=session,id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def is_admin(user: tblUser=Depends(get_current_user)):
    if user.IsAdmin != True:
        raise HTTPException(status_code=403, detail="Admins only")
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expiration = datetime.now(timezone.utc) + expires_delta
    else: 
        expiration = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_user_or_404(username: str, session: SessionDep):
    user = get_user(username=username, session=session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return user

def not_me_or_400(user: tblUser, me: tblUser) -> bool:
    if user.UserId == me.UserId: 
        raise HTTPException(400, detail="Cannot perform this action on yourself.")
    return True

def database_delete(session: SessionDep, user: tblUser):
    session.delete(user)
    session.commit()

def database_save(session: SessionDep, dbinstance):
    session.add(dbinstance)
    session.commit()