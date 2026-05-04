

from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

from jwt import PyJWTError, encode
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

from .database import SessionDep
from .models import User, UserInDB

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
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt