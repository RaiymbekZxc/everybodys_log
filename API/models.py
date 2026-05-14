

from sqlmodel import SQLModel, Field
from pydantic import BaseModel 
from datetime import datetime, timezone
from enum import Enum


class UpdateType(Enum):
    password = "password"
    username = "username"

class UserUpdate(BaseModel):
    TypeOfInteraction: UpdateType
    Username: str | None = None
    Password: str | None = None
    NewPassword: str | None = None 

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    Username: str
    Password: str 
    Email: str
    IsActive: bool | None = False

class User(SQLModel):
    UserId: int = Field(primary_key=True)
    Username: str = Field(default=None, unique=True)
    Email: str = Field(default=None, unique=True)
    IsActive: bool = Field(default=True)
    IsAdmin: bool = Field(default=False)
    DateRegistered: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

class tblUser(User, table=True):
    hashed_password: str

class tblCategory(SQLModel, table=True):
    CategoryId: int = Field(default=None, primary_key=True)
    Name: str = Field(default=None, unique=True)
    Description: str = Field(default="No description.")

class tblActivity(SQLModel, table=True):
    ActivityId: int = Field(primary_key=True)
    UserId: int = Field(default = None, foreign_key="tbluser.UserId")
    CategoryId: int = Field(default = None, foreign_key="tblcategory.CategoryId")
    Description: str = Field(default="No description.")
    DateLogged: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
