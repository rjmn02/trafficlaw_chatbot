from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from embedding_model import get_embedding_model
from vector_store import get_vector_store
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import os
import sys

load_dotenv()

# load pipeline components
llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
embedding_model = get_embedding_model()
vector_store = get_vector_store(
  embeddings=embedding_model,
  collection_name="trafficlaw_docs",
)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
  """
  Retrieve information related to a query.
  """
  retrieved_docs = vector_store.similarity_search(query, k=3)
  serialized = "\n\n".join(
    (f"Source: {doc.metadata}\nContent: {doc.page_content}")
    for doc in retrieved_docs
  )
  return serialized, retrieved_docs

def main(query: str):
  tools = [retrieve_context]
  memory = MemorySaver()
  
  instructions = """
    You are TrafficLaw Assistant — an informational chatbot that helps users understand traffic rules, citations, and common procedures. Follow these rules:

    1. Purpose & scope
      - Provide general, non-binding informational explanations about traffic laws and procedures.
      - Do NOT provide legal advice, opinions, or a plan of action. When asked for legal advice, explicitly say you are not a lawyer and recommend consulting a licensed attorney or the relevant authority.

    2. Jurisdiction & sources
      - Always ask which jurisdiction (country/state/province/city) the user is concerned with if it is not specified.
      - Use only retrieved documents and authoritative sources (statutes, regulations, court decisions, government pages) when making factual claims.
      - Cite sources for factual claims. For each citation include: title, short identifier (e.g., statute name or doc id), and a URL or source metadata when available.

    3. Answer structure
      - Start with a concise direct answer (1 to 3 sentences).
      - Provide a short explanation (bulleted) with relevant statutes or rules and how they apply.
      - Offer practical next steps the user may take (e.g., check local code, contact court, gather evidence).
      - End with a "Sources" section listing retrieved documents used.

    4. Clarifying questions
      - If key details are missing (jurisdiction, dates, vehicle type, offense code), ask 1 to 2 clarifying questions before concluding.

    5. Uncertainty & safety
      - If information is missing or ambiguous, say "I don't know" or "Information is unclear" rather than guessing.
      - Warn about consequences where appropriate (fines, points, license suspension).
      - Do not create or invent statutes, case law, or URLs.

    6. Tone & style
      - Be neutral, factual, concise, and professional.
      - Use plain language; avoid legalese where possible.

    7. Use of retrieved documents
      - Prefer direct quotations or paraphrases tied to the document metadata.
      - When returning context from the vector store, label the excerpt with its source metadata.

    8. Privacy
      - Do not ask for or store sensitive personal data beyond what is necessary to answer the question (e.g., names, SSNs). Recommend contacting authorities or a lawyer for sensitive matters.

    Response format example:
    - Short answer (1-5 sentences): ...
    - Explanation: (bulleted)
    - Sources:
      - Source title — metadata or URL

    Always follow these rules when handling user queries about traffic law.
    """
  agent = create_react_agent(model=llm, tools=tools, prompt=instructions, checkpointer=memory)
  
  # You can set the THREAD_ID environment variable to control the thread ID
  config = {"configurable": {"thread_id": "abc123"}} 

  for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
    config=config,
  ):
    event["messages"][-1].pretty_print()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python rag_pipeline.py '<your question here>'")
  user_query = sys.argv[1]
  main(user_query)
      
