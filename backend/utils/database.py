import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with SessionLocal() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]