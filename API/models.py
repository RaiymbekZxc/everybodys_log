

from sqlmodel import SQLModel, Field
from pydantic import BaseModel 
from pwdlib import PasswordHash
from .auth import DUMMY_HASH

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    name: str
    email: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str


class UserTable(SQLModel, table=True):
    username: str = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str = Field(default=DUMMY_HASH)

