import os
from groq import Groq
from sqlalchemy import select
from memory import ConversationMemory
from utils.database import AsyncSessionDep
from models.document import Document
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from schemas.query import QueryRequest, QueryResponse


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_TOP_K = 50

# --- Pre-load models and clients for efficiency ---
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
groq_client = Groq(api_key=GROQ_API_KEY)
# --- End of pre-loading ---


async def similarity_search(
  query: str,
  db: AsyncSessionDep,
  top_k: Optional[int] = DEFAULT_TOP_K,
) -> List[DocumentInDB]:
  query_embedding = embedding_model.encode(query, normalize_embeddings=True).tolist()

  try:
    # PostgreSQL pgvector cosine distance operator <=>
    stmt = select(Document).order_by(Document.embedding.op("<=>")(query_embedding)).limit(top_k)

    result = await db.execute(stmt)
    results = result.scalars().all()

    return results

  except Exception as e:
    print(f"Error during similarity search: {e}")
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
    # Include ALL history instead of just the last 4 messages
    history_lines = []
    for msg in history:
      role = msg["role"].upper()
      content = msg["content"]
      history_lines.append(f"{role}: {content}")
    conversation = "\nPrevious conversation:\n" + "\n".join(history_lines) + "\n"

  template = f"""You are an expert assistant on Philippine traffic laws and vehicle regulations.

{conversation if conversation else ""}

CONTEXT DOCUMENTS:
{context_text}

INSTRUCTIONS:
- Answer using ONLY the provided context
- Include specific amounts, penalties, and time periods exactly as stated
- Structure multi-part answers clearly (First offense: X, Second offense: Y)
- State if information is missing from the context
- Do not add information beyond what is provided
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

  completion = groq_client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": augmented_prompt}],
    max_completion_tokens=1024,
    stream=False,
    temperature=0.3,
    top_p=0.9,
  )
  llm_answer = completion.choices[0].message.content

  # Extract contexts for response (if still needed)
  contexts = [doc.content for doc in retrieved_docs]
  return QueryResponse(answer=llm_answer, retrieved_docs=contexts)
