from sqlalchemy import select, func
from utils.database import AsyncSessionDep
from models.base import Document  # ADDED IMPORT
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TOP_K = 3

async def similarity_search(query: str, db: AsyncSessionDep, top_k: Optional[int] = DEFAULT_TOP_K) -> List[DocumentInDB]:
  model = SentenceTransformer(EMBEDDING_MODEL)
  query_embedding = model.encode(query)

  try:
    stmt = (
      select(Document)
      .order_by(Document.embedding.op("<->")(query_embedding))  # Using the <-> operator for cosine distance
      .limit(top_k)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
  except Exception as e:
    print(f"Error during similarity search: {e}")
    return []

async def prompt_augmentation(query: str, db: AsyncSessionDep):
  pass

async def generate_response(query: str, db: AsyncSessionDep):
  pass