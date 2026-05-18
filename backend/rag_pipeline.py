import logging
from sqlalchemy import select
from memory import ConversationMemory
from utils.database import SessionDep
from models.document import Document
from schemas.document import DocumentInDB
from typing import List, Optional
from schemas.query import QueryRequest, QueryResponse
from utils.models import embedding_model, groq_client

logger = logging.getLogger(__name__)


LLM_MODEL = "llama-3.1-8b-instant"
DEFAULT_TOP_K = 20


def similarity_search(
    query: str,
    db: SessionDep,
    top_k: Optional[int] = DEFAULT_TOP_K,
) -> List[DocumentInDB]:
    query_embedding = embedding_model.encode(
        query, normalize_embeddings=True, show_progress_bar=False
    ).tolist()

    try:
        stmt = select(Document).order_by(Document.embedding.op("<=>")(query_embedding)).limit(top_k)
        result = db.execute(stmt)          # no await
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Error during similarity search: {e}")
        return []


def build_prompt(query: str, documents: List[DocumentInDB], history: List[dict]) -> str:
    if documents:
        numbered_contexts = []
        for doc in documents:
            doc_name = doc.file_source if doc.file_source else "Unknown Document"
            numbered_contexts.append(f"[Document {doc_name}: ]\n{doc.content}")
        context_text = "\n\n".join(numbered_contexts)
    else:
        context_text = "No relevant documents found."

    conversation = ""
    if history:
        recent_history = history[-6:] if len(history) > 6 else history
        history_lines = [f"{msg['role'].upper()}: {msg['content']}" for msg in recent_history]
        conversation = "\nPrevious conversation:\n" + "\n".join(history_lines) + "\n"

    return f"""You are a helpful and friendly expert assistant on Philippine traffic laws and vehicle regulations.

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


def generate_response(
    query_request: QueryRequest, db: SessionDep, memory: ConversationMemory = None
) -> QueryResponse:
    query = query_request.query
    retrieved_docs = similarity_search(query, db)      # no await

    history = memory.get_history() if memory else []
    augmented_prompt = build_prompt(query, retrieved_docs, history)

    completion = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": augmented_prompt}],
        max_completion_tokens=512,
        stream=False,
        temperature=0.3,
        top_p=0.9,
        timeout=30.0,
    )
    llm_answer = completion.choices[0].message.content

    contexts = [doc.content for doc in retrieved_docs]
    return QueryResponse(answer=llm_answer, retrieved_docs=contexts)