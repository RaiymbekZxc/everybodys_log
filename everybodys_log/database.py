from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv

load_dotenv() #.env file

database_url = os.getenv("DB_URL")
engine = create_engine(database_url, echo=True)

SQLModel.metadata.create_all(engine)


