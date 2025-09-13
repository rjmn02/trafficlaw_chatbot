from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from embedding_model import get_embedding_model
from vector_store import get_vector_store
from langchain_core.tools import tool
from langchain.agents import create_agent

import os

load_dotenv()

# load pipeline components
llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
embedding_model = get_embedding_model()
vector_store = get_vector_store(
  embeddings=embedding_model,
  collection_name="trafficlaw_docs",
)

