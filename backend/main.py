import logging
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import select, func
from schemas.query import QueryRequest, QueryResponse, ClearSessionResponse 
from utils.database import engine, async_session, AsyncSessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import Base
from models.document import Document
from fastapi.middleware.cors import CORSMiddleware
from data_preprocessing import (
  clean_document_contents,
  embed_documents,
  load_documents,
  chunk_documents,
)
from rag_pipeline import generate_response
from memory import ConversationMemory


session_memories = {}
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) 
logger = logging.getLogger(__name__)

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

# Get allowed origins from environment variable or default to localhost for development
def get_allowed_origins():
  env_origins = os.getenv("ALLOWED_ORIGINS")
  if env_origins:
    return [origin.strip() for origin in env_origins.split(",")]
  # Default to localhost origins for development
  return [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:3001",  # Next.js API
    "http://localhost:5173",  # Vite/other dev servers
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
  ]

app.add_middleware(
  CORSMiddleware,
  allow_origins=get_allowed_origins(),
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
  expose_headers=["set-cookie"],
)


async def ingest_documents(session: AsyncSession):
  try:
    existing = (await session.execute(select(func.count()).select_from(Document))).scalar() or 0
    if existing > 0:
      logger.info("Documents already ingested. Skipping.")
      return

    docs = load_documents()
    docs = clean_document_contents(docs)
    docs = chunk_documents(docs)
    docs = await embed_documents(docs)

    session.add_all(docs)
    await session.commit()
    logger.info(f"Ingested {len(docs)} chunks.")
  except Exception as e:
    await session.rollback()
    logger.exception(f"Ingestion error: {e}")


@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(query_request: QueryRequest, db: AsyncSessionDep = AsyncSessionDep()):
  # Retrieve or create a conversation memory for the current session_id
  if query_request.session_id not in session_memories:
    session_memories[query_request.session_id] = ConversationMemory()
  
  memory = session_memories[query_request.session_id]
  
  # Generate response with RAG pipeline
  response = await generate_response(query_request, db, memory)
  
  # Update conversation history
  memory.add_message("user", query_request.query)
  memory.add_message("assistant", response.answer)
  
  return response


@app.delete("/sessions/{session_id}", response_model=ClearSessionResponse)
async def clear_session_endpoint(session_id: str):
  # Validate session_id format
  if not session_id or len(session_id) > 100:
    return ClearSessionResponse(cleared=False, message="Invalid session ID")
  if not all(c.isalnum() or c in '-_.' for c in session_id):
    return ClearSessionResponse(cleared=False, message="Invalid session ID format")
  
  if session_id in session_memories:
    del session_memories[session_id]
    return ClearSessionResponse(cleared=True, message=f"Session {session_id} cleared successfully")
  else:
    return ClearSessionResponse(cleared=False, message=f"Session {session_id} not found")
