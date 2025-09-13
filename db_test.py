import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# print("DATABASE_URL ->", repr(os.getenv("DATABASE_URL")))

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    print("Connected to:", conn.engine.url)
