from lib2to3.fixes.fix_input import context
import os
from groq import Groq
from sqlalchemy import select, func
from memory import ConversationMemory
from utils.database import AsyncSessionDep
from models.base import Document  # ADDED IMPORT
from schemas.document import DocumentInDB
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from langchain.prompts import ChatPromptTemplate


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

async def prompt_augmentation(query: str, contexts: str, history: List[str]) -> str:
  template = """
  You are a Philippine Traffic Law Chatbot that provides reliable, contextually grounded information about traffic laws and vehicle regulations in the Philippines.
  Follow these rules strictly when answering:

  - Use only the provided context to generate responses. If the answer is not in the context, say: “I don't know the answer based on Philippine traffic laws.”
  - Keep answers concise (1-5 sentences).
  - Always stay within the scope: Philippine traffic and vehicle regulations only. Do not provide unrelated legal or personal advice.
  - Be clear, neutral, and user-friendly in tone.
  - Always end responses with: “Thanks for asking!”
  - If necessary, remind users: “This chatbot is for informational purposes only and not a substitute for professional legal advice.”

  Context:
  {context}

  User Query:
  {query}

  Answer:"""
  
  prompt = ChatPromptTemplate.from_template(template)

  return prompt

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
