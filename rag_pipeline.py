import os
from groq import Groq
from sqlalchemy import select
from memory import ConversationMemory, Message
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

# ---- Prompt Step with history ----
def build_prompt(query: str, contexts: List[DocumentInDB], history: List[Message]) -> str:
  context_text = "\n\n".join([doc.content for doc in contexts]) if contexts else "No relevant documents found."

  # Format conversation history (last few exchanges)
  history_text = ""
  for msg in history:
      role = "User" if msg["role"] == "user" else "Assistant"
      history_text += f"{role}: {msg['content']}\n"

  template = """
  You are a Philippine Traffic Law Chatbot that provides reliable, contextually grounded information about traffic laws and vehicle regulations in the Philippines.

  Rules:
  - Use only the provided context to generate responses. If the answer is not in the context, say: “I don't know the answer based on Philippine traffic laws.”
  - Keep answers concise (1-5 sentences).
  - Stay within Philippine traffic and vehicle regulations only.
  - Always end responses with: “Thanks for asking!”
  - If necessary, remind users: “This chatbot is for informational purposes only and not a substitute for professional legal advice.”

  Conversation so far:
  {history}

  Context:
  {context}

  User Query:
  {query}

  Answer:
  """
  prompt = ChatPromptTemplate.from_template(template)
  return prompt.format(history=history_text, context=context_text, query=query)


async def generate_response(query_request: QueryRequest, db: AsyncSessionDep, memory: ConversationMemory) -> QueryResponse:
    query = query_request.query
    retrieved_docs = await similarity_search(query, db)
    contexts = [doc.content for doc in retrieved_docs]

    augmented_prompt = build_prompt(query, contexts, memory.get_history())

    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": augmented_prompt}],
        max_completion_tokens=8192,
        temperature=1,
        top_p=1,
        stream=False,
    )
    llm_answer = completion.choices[0].message["content"]

    # Record interaction
    memory.add_message(role="user", content=query, context=None)
    memory.add_message(role="assistant", content=llm_answer, context=contexts)

    return QueryResponse(answer=llm_answer, retrieved_docs=contexts)

