

from sqlmodel import SQLModel, Field
from pydantic import BaseModel 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserCreate(BaseModel):
    username: str
    password: str 
    email: str
    name: str
    disabled: bool | None = False

class User(SQLModel):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(default=None)
    name: str = Field(default="No Name")
    email: str = Field(default=None)
    disabled: bool = Field(default=False)

class UserInDB(User, table=True):
    hashed_password: str
