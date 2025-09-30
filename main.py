from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy import select, func
from schemas.document import DocumentBase
from utils.database import engine, AsyncSessionDep
from models.base import Base, Document  # ADDED IMPORT
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from data_preprocessing import clean_document_contents, embed_documents, load_documents, chunk_documents, embed_documents
  

# The first part of the function, before the yield, will be executed before the application starts.
# And the part after the yield will be executed after the application has finished.
@asynccontextmanager
async def lifespan(app: FastAPI):
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
    
  await ingest_documents()
  yield
  await engine.dispose()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["set-cookie"]
)

async def ingest_documents(db: AsyncSessionDep):
  
  count_documents = select(func.count()).select_from(Document)
  
  documents: List[DocumentBase] = load_documents()
  cleaned_docs: List[DocumentBase] = clean_document_contents(documents)
  chunked_docs: List[DocumentBase] = chunk_documents(cleaned_docs)
  embedded_documents: List[DocumentBase] = await embed_documents(chunked_docs)

  # Store embedded_documents in the database
  try:
    result = await db.execute(count_documents)
    total_documents = result.scalar()
    if total_documents > 0:
      print("Documents already ingested. Skipping ingestion.")
      return
    db.add_all(embedded_documents)
    await db.commit()
  except Exception as e:
    await db.rollback()
    print(f"Error storing documents: {e}")
  
  
  
