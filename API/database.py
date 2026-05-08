from typing import Annotated

from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from pwdlib import PasswordHash

from .models import UserInDB 

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args)
password_hash = PasswordHash.recommended()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]