import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import select, func
from schemas.query import QueryRequest, QueryResponse, ClearSessionResponse 
from utils.database import engine, async_session, AsyncSessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import Base  # ADDED IMPORT
from models.document import Document  # NEW: correct source of Document
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

origins = [
  "http://localhost:3000",  # Next.js frontend
  "http://localhost:3001",  # Next.js API
  "http://localhost:5173",  # Vite/other dev servers
  "http://127.0.0.1:8000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
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
  try:
    memory = session_memories.setdefault(
      query_request.session_id, ConversationMemory(max_length=10)
    )
  except Exception as e:
    logger.exception("Failed to initialize session memory for session_id=%s", getattr(query_request, "session_id", None))
    raise HTTPException(status_code=500, detail="Failed to initialize session memory") from e
  
  # Add user query to memory
  try:
    memory.add_message("user", query_request.query)
  except Exception as e:
    logger.exception("Failed to add user message to memory for session_id=%s", query_request.session_id)
    raise HTTPException(status_code=500, detail="Failed to add user message to memory") from e
  
  # Generate response using memory context
  try:
    response: QueryResponse = await generate_response(query_request, db, memory)
  except Exception as e:
    logger.exception("Failed to generate response for session_id=%s", query_request.session_id)
    raise HTTPException(status_code=500, detail="Failed to generate response") from e
  
  # Add assistant response to memory
  try:
    memory.add_message("assistant", response.answer)
  except Exception as e:
    logger.exception("Failed to add assistant message to memory for session_id=%s", query_request.session_id)
    raise HTTPException(status_code=500, detail="Failed to add assistant message to memory") from e
  
  return response

# Endpoint to clear or delete session memory
@app.delete("/sessions/{session_id}", response_model=ClearSessionResponse)
async def clear_session(session_id: str):
  removed = session_memories.pop(session_id, None)
  if removed is None:
    return ClearSessionResponse(cleared = False, message = "Session ID not found.")
  return ClearSessionResponse(cleared = True, message = "Session memory cleared.")