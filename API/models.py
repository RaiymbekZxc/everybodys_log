

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    username: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    password: str
