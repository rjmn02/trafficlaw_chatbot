import os
from groq import Groq
from sqlalchemy import func, select
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
    # PostgreSQL pgvector cosine distance operator
    stmt = select(Document).order_by(Document.embedding.op("<=>")(query_embedding)).limit(top_k)

    result = await db.execute(stmt)
    results = result.scalars().all()

    return results

  except Exception as e:
    print(f"Error during similarity search: {e}")
    return []


# ---- Prompt Step with history ----
def build_prompt(query: str, contexts: List[str], history: List[dict]) -> str:
  # Improved prompt with better instructions
  if contexts:
    numbered_contexts = []
    for i, ctx in enumerate(contexts):
      numbered_contexts.append(f"[Document {i + 1}]\n{ctx}")
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
1. Answer the question completely and accurately using ONLY the information in the context documents
2. Include ALL relevant details: specific amounts, time periods, conditions, and penalties
3. Structure multi-part answers clearly (e.g., "First offense: X, Second offense: Y")
4. If information is missing, state what is not covered in the documents
5. Do not add information not present in the context

QUESTION: {query}

ANSWER:"""

  return template


async def generate_response(
  query_request: QueryRequest, db: AsyncSessionDep, memory: ConversationMemory = None
) -> QueryResponse:
  query = query_request.query
  retrieved_docs = await similarity_search(query, db)
  contexts = [doc.content for doc in retrieved_docs]

  # Use conversation history if available
  history = memory.get_history() if memory else []
  augmented_prompt = build_prompt(query, contexts, history)

  completion = groq_client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": augmented_prompt}],
    max_completion_tokens=1024,
    stream=False,
    temperature=0.3,
    top_p=0.9,
  )
  llm_answer = completion.choices[0].message.content

  return QueryResponse(answer=llm_answer, retrieved_docs=contexts)
