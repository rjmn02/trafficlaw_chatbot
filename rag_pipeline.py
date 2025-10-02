import os
from groq import Groq
from sqlalchemy import select, func
from memory import ConversationMemory
from utils.database import AsyncSessionDep
from models.base import Document  # ADDED IMPORT
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
DEFAULT_TOP_K = 3

memory = ConversationMemory()

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

async def prompt_augmentation(query: str, contexts: List[DocumentInDB], history: List[str]) -> str:
  # Format contexts as readable text
  formatted_contexts = "\n".join([
    f"Content: {doc.content}\nMetadata: {doc.metadata}" for doc in contexts
  ])
  
  # Include history for context
  history_str = "\n".join(history) if history else "No prior conversation."
  
  augmented_prompt = f"""
  Philippine TrafficLaw Assistant — provide general, non-binding information about traffic rules and procedures. Do not give legal advice; if asked, say you are not a lawyer and recommend consulting an attorney or the relevant authority.

  Jurisdiction & sources:
  - Ask for the jurisdiction if not specified.
  - Make factual claims only from retrieved documents and authoritative sources.
  - For each claim, cite: title, short identifier (e.g., statute name/doc id), and URL/metadata.
  - Prefer brief quotes/paraphrases tied to source metadata. Do not invent statutes, cases, or URLs. If no relevant sources are retrieved, say so and ask to refine the query.

  Clarifying questions:
  - If key details are missing (jurisdiction, dates, vehicle type, offense code), ask 1-2 questions before concluding.

  Uncertainty & safety:
  - Say "I don't know" or "Information is unclear" rather than guessing.
  - Note possible consequences when relevant (fines, points, suspension).

  Tone & privacy:
  - Neutral, factual, concise, plain language; avoid legalese.
  - Do not request/store sensitive personal data beyond what is necessary.

  Response format example:
  - Short answer (1-5 sentences): ...
  - Explanation: (bulleted)
  - Sources:
    - Source title — metadata or URL

  Conversation History:
  {history_str}

  Answer the query based on the following context from retrieved documents:
  
  {formatted_contexts}
  
  Query: 
  
  {query}
    
  """
  
  return augmented_prompt


async def generate_response(query: str, db: AsyncSessionDep):
  contexts = await similarity_search(query, db)
  augmented_prompt = await prompt_augmentation(query, contexts)

  client = Groq(os.getenv("GROQ_API_KEY"))
  completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "user",
        "content": augmented_prompt
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
  )

  for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
