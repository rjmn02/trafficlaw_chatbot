from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import select, func
from schemas.query import QueryRequest, QueryResponse
from utils.database import engine, async_session, AsyncSessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import Base  # ADDED IMPORT
from models.document import Document  # NEW: correct source of Document
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from data_preprocessing import clean_document_contents, embed_documents, load_documents, chunk_documents, embed_documents
from rag_pipeline import generate_response
from memory import ConversationMemory
# The first part of the function, before the yield, will be executed before the application starts.
# And the part after the yield will be executed after the application has finished.
@asynccontextmanager
async def lifespan(app: FastAPI):
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  
  async with async_session() as session:
    await ingest_documents(session)
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

async def ingest_documents(session: AsyncSession):
  try:
    existing = (
      await session.execute(
        select(func.count()).select_from(Document))).scalar() or 0
    if existing > 0:
      print("Documents already ingested. Skipping.")
      return

    docs = load_documents()
    docs = clean_document_contents(docs)
    docs = chunk_documents(docs)
    docs = await embed_documents(docs)

    session.add_all(docs)
    await session.commit()
    print(f"Ingested {len(docs)} chunks.")
  except Exception as e:
    await session.rollback()
    print(f"Ingestion error: {e}")
  
memory = ConversationMemory(max_length=10)
@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(query_request: QueryRequest, db: AsyncSessionDep = AsyncSessionDep()):
  # Add user query to memory
  memory.add_message("user", query_request.query)
  
  # Generate response using memory context
  response: QueryResponse = await generate_response(query_request, db, memory)
  
  # Add assistant response to memory
  memory.add_message("assistant", response.answer)
  
  return response

