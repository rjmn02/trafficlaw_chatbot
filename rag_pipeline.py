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
  agent = create_react_agent(model=llm, tools=tools, checkpointer=memory)
  
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
      
