import os
from groq import Groq
from huggingface_hub import InferenceClient

# Constants for embedding and vector database
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Response generation constants
LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TOP_K = 15

# Preprocessing constants
CHUNK_SIZE = 1000
OVERLAP = 200

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is not set")

hf_client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
  )

groq_client = Groq(api_key=GROQ_API_KEY)
