import os
import logging
from groq import Groq
from sqlalchemy import select
from memory import ConversationMemory
from utils.database import AsyncSessionDep
from models.document import Document
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from schemas.query import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_TOP_K = 20

# --- Pre-load models and clients for efficiency ---
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
groq_client = Groq(api_key=GROQ_API_KEY)
# --- End of pre-loading ---


async def similarity_search(
  query: str,
  db: AsyncSessionDep,
  top_k: Optional[int] = DEFAULT_TOP_K,
) -> List[DocumentInDB]:
  # Generate embedding (blocking I/O, but fast with pre-loaded model)
  query_embedding = embedding_model.encode(query, normalize_embeddings=True, show_progress_bar=False).tolist()

  try:
    # PostgreSQL pgvector cosine distance operator <=>
    # Ensure you have an index on the embedding column for fast searches:
    # CREATE INDEX ON document USING ivfflat (embedding vector_cosine_ops);
    stmt = select(Document).order_by(Document.embedding.op("<=>")(query_embedding)).limit(top_k)

    result = await db.execute(stmt)
    results = result.scalars().all()

    return results

  except Exception as e:
    # Log error but don't expose details to client
    logger.error(f"Error during similarity search: {e}")
    return []


# ---- Prompt Step with history ----
def build_prompt(query: str, documents: List[DocumentInDB], history: List[dict]) -> str:
  # Improved prompt with better instructions and document sources
  if documents:
    numbered_contexts = []
    for i, doc in enumerate(documents):
      doc_name = doc.file_source if doc.file_source else "Unknown Document"
      numbered_contexts.append(f"[Document {doc_name}: ]\n{doc.content}")
    context_text = "\n\n".join(numbered_contexts)
  else:
    context_text = "No relevant documents found."

  conversation = ""
  if history:
    # Limit to last 6 messages (3 exchanges) to keep prompt size manageable
    recent_history = history[-6:] if len(history) > 6 else history
    history_lines = []
    for msg in recent_history:
      role = msg["role"].upper()
      content = msg["content"]
      history_lines.append(f"{role}: {content}")
    conversation = "\nPrevious conversation:\n" + "\n".join(history_lines) + "\n"

  template = f"""You are a helpful and friendly expert assistant on Philippine traffic laws and vehicle regulations.

{conversation if conversation else ""}

CONTEXT DOCUMENTS:
{context_text}

INSTRUCTIONS:
- If the user greets you or makes casual conversation, respond warmly and briefly, then invite them to ask about traffic laws
- For traffic law questions: Answer using ONLY the provided context documents
- Include specific amounts, penalties, and time periods exactly as stated
- Structure multi-part answers clearly (First offense: X, Second offense: Y)
- If the question isn't about traffic laws or no relevant context is found, politely explain that you specialize in Philippine traffic laws
- Do not add information beyond what is provided in the context
- Answer concisely and clearly

QUESTION: {query}

ANSWER:"""

  return template


async def generate_response(
  query_request: QueryRequest, db: AsyncSessionDep, memory: ConversationMemory = None
) -> QueryResponse:
  query = query_request.query
  retrieved_docs = await similarity_search(query, db)

  # Use conversation history if available
  history = memory.get_history() if memory else []
  augmented_prompt = build_prompt(query, retrieved_docs, history)  # Pass entire document objects

  # Use timeout to prevent hanging requests
  completion = groq_client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": augmented_prompt}],
    max_completion_tokens=512,
    stream=False,
    temperature=0.3,
    top_p=0.9,
    timeout=30.0,  # 30 second timeout
  )
  llm_answer = completion.choices[0].message.content

  # Extract contexts for response (if still needed)
  contexts = [doc.content for doc in retrieved_docs]
  return QueryResponse(answer=llm_answer, retrieved_docs=contexts)
