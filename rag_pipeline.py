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

# Configuration constants
MODEL_NAME = "llama-3.1-8b-instant"
MODEL_PROVIDER = "groq"
COLLECTION_NAME = "trafficlaw_docs"
RETRIEVAL_K = 3
DEFAULT_THREAD_ID = "abc123"



# load pipeline components
llm = init_chat_model(MODEL_NAME, model_provider=MODEL_PROVIDER)
embedding_model = get_embedding_model()
vector_store = get_vector_store(
  embeddings=embedding_model,
  collection_name=COLLECTION_NAME,
)


# Retriever tool; LLM will use this to fetch relevant documents
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
  """
  Retrieve information related to a query.
  """
  retrieved_docs = vector_store.similarity_search(query, k=RETRIEVAL_K)
  serialized = "\n\n".join(
    (f"Source: {doc.metadata}\nContent: {doc.page_content}")
    for doc in retrieved_docs
  )
  return serialized, retrieved_docs


def stream(agent, config: dict, query: str) -> None:
  for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
    config=config,
  ):
    event["messages"][-1].pretty_print()
    
def make_config(thread_id: str) -> dict:
  return {"configurable": {"thread_id": thread_id}}


def build_agent(thread_id: str = DEFAULT_THREAD_ID):
  instructions = """
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

    Always follow these rules when handling user queries about traffic law.
    """
  tools = [retrieve_context]
  memory = MemorySaver()
  agent = create_react_agent(model=llm, tools=tools, prompt=instructions, checkpointer=memory)
  config = make_config(thread_id)
  
  return agent, config


def run_agent(agent, config: dict) -> None:
  print("Welcome to the TrafficLaw Assistant! Type 'exit' to quit.")
  while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['exit', 'quit']:
      print("Goodbye!")
      break
    
    stream(agent=agent, config=config, query=user_input)
    

def run_agent_once(agent, config: dict, query: str) -> None:
  stream(agent=agent, config=config, query=query)


if __name__ == "__main__":
  agent, config = build_agent()
  if len(sys.argv) == 2:
    user_query = sys.argv[1]
    run_agent_once(agent=agent, config=config, query=user_query)
  else:
    run_agent(agent=agent, config=config)