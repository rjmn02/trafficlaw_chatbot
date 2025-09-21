from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from embedding_model import get_embedding_model
from vector_store import get_vector_store
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
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
  Retrieve the top 3 relevant traffic law documents for the given query.
  Returns a serialized string for display and the raw document objects for citation.
  """
  retrieved_docs = vector_store.similarity_search(query, k=3)
  serialized = "\n\n".join(
    (f"Source: {doc.metadata}\nContent: {doc.page_content}")
    for doc in retrieved_docs
  )
  return serialized, retrieved_docs

def main(query: str):
    tools = [retrieve_context]
    prompt = (
        "You can call a tool that returns relevant passages from a collection of traffic law documents. "
        "Always call the tool first to fetch supporting evidence before giving response "
        "If no evidence, say you lack sufficient context."
    )
    agent = create_react_agent(model=llm, tools=tools, prompt=prompt)
    
    for event in agent.stream(
      input = {"messages": [{"role": "user", "content": query}]},
      stream_mode="updates",
    ):
      print(event)
        
