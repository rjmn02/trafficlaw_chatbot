import os
from groq import Groq
from sqlalchemy import select
from memory import ConversationMemory
from utils.database import AsyncSessionDep
from models.document import Document
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from langchain.prompts import ChatPromptTemplate
from schemas.query import QueryRequest, QueryResponse


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_TOP_K = 3

# --- Pre-load models and clients for efficiency ---
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
groq_client = Groq(api_key=GROQ_API_KEY)
# --- End of pre-loading ---


async def similarity_search(query: str, db: AsyncSessionDep, top_k: Optional[int] = DEFAULT_TOP_K) -> List[DocumentInDB]:
  query_embedding = embedding_model.encode(query)
  
  # Similarity Search Operators:

  #   pgvector provides operators to calculate different similarity metrics:
  #       <->: Euclidean distance (L2 distance)
  #       <#>: Inner product
  #       <=>: Cosine distance
  
  try:
    stmt = (
      select(Document)
      .order_by(Document.embedding.op("<=>")(query_embedding))  # Using the <=> operator for cosine distance
      .limit(top_k)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
  except Exception as e:
    print(f"Error during similarity search: {e}")
    return []

# ---- Prompt Step with history ----
def build_prompt(query: str, contexts: List[str], history: List[dict]) -> str:
  context_text = "\n\n".join(contexts) if contexts else "No relevant documents found."
  
  # Format conversation history
  conversation = ""
  if history:
    for message in history:
      role = message["role"]
      content = message["content"]
      conversation += f"{role}: {content}\n"
  
  template = """
  You are a Philippine Traffic Law Chatbot that provides reliable, contextually grounded information about traffic laws and 
  vehicle regulations in the Philippines.

  Rules:
  - Use only the provided context to generate responses. If the answer is not in the context, say: 
    "I don't know the answer based on Philippine traffic laws."
  - Keep answers concise (1-5 sentences).
  - Stay within Philippine traffic and vehicle regulations only.
  - Cite specific laws, articles, or sections when relevant.

  Context:
  {context}
  
  Conversation History:
  {history}

  User Query:
  {query}

  Answer:
  """
  prompt = ChatPromptTemplate.from_template(template)
  return prompt.format(context=context_text, history=conversation, query=query)


async def generate_response(
  query_request: QueryRequest, 
  db: AsyncSessionDep,
  memory: ConversationMemory = None
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
