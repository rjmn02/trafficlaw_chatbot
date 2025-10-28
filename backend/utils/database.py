import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
# Create session factory ONCE
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Then, in your dependency
async def get_session():
  async with async_session() as session:
     yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]