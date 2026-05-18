import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from httpcore import request
from sqlalchemy import select, func
from schemas.query import QueryRequest, QueryResponse, ClearSessionResponse
from utils.database import engine, SessionLocal, SessionDep
from sqlalchemy.orm import Session
from models.base import Base
from models.document import Document
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from data_preprocessing import (
    clean_document_contents,
    embed_documents,
    load_documents,
    chunk_documents,
)
from rag_pipeline import generate_response
from memory import ConversationMemory
from cachetools import TTLCache
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException


# --- Auth ---
APP_API_KEY = os.getenv("APP_API_KEY")
if not APP_API_KEY:
    raise RuntimeError("APP_API_KEY is not set")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Security(api_key_header)):
    if key != APP_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# --- Rate limiter ---
limiter = Limiter(key_func=get_remote_address)


# --- Session memory (TTL: 1 hour, max 1000 sessions) ---
session_memories: TTLCache = TTLCache(maxsize=1000, ttl=3600)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    with SessionLocal() as session:
        ingest_documents(session)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter


# --- Rate limit exceeded handler ---
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."}
    )


# --- CORS ---
def get_allowed_origins():
    env_origins = os.getenv("ALLOWED_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]
    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["set-cookie"],
)


def ingest_documents(session: Session):
    try:
        existing = session.execute(select(func.count()).select_from(Document)).scalar() or 0
        if existing > 0:
            logger.info("Documents already ingested. Skipping.")
            return

        docs = load_documents()
        docs = clean_document_contents(docs)
        docs = chunk_documents(docs)
        docs = embed_documents(docs)

        session.add_all(docs)
        session.commit()
        logger.info(f"Ingested {len(docs)} chunks.")
    except Exception as e:
        session.rollback()
        logger.exception("Ingestion error")   # don't log `e` directly, exception() captures it


@app.post("/chat", response_model=QueryResponse)
@limiter.limit("10/minute")
def chat_endpoint(
    request: Request,                          # required by slowapi
    query_request: QueryRequest,
    db: SessionDep,
    _: str = Security(verify_api_key),         # auth check
):
    if query_request.session_id not in session_memories:
        session_memories[query_request.session_id] = ConversationMemory()

    memory = session_memories[query_request.session_id]
    response = generate_response(query_request, db, memory)

    memory.add_message("user", query_request.query)
    memory.add_message("assistant", response.answer)
    print("Expected:", os.getenv("APP_API_KEY"))
    print("Received:", request.headers.get("X-API-Key"))

    return response


@app.delete("/sessions/{session_id}", response_model=ClearSessionResponse)
def clear_session_endpoint(
    session_id: str,
    _: str = Security(verify_api_key),         # auth check
):
    # validation already done in QueryRequest, but session_id here is a path param
    if not session_id or len(session_id) > 100:
        return ClearSessionResponse(cleared=False, message="Invalid session ID")
    if not all(c.isalnum() or c in '-_.' for c in session_id):
        return ClearSessionResponse(cleared=False, message="Invalid session ID format")

    if session_id in session_memories:
        del session_memories[session_id]
        return ClearSessionResponse(cleared=True, message=f"Session {session_id} cleared successfully")

    return ClearSessionResponse(cleared=False, message=f"Session {session_id} not found")