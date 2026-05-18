import os
from groq import Groq
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import torch

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
device = "cuda" if torch.cuda.is_available() else "cpu"

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=device)
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
groq_client = Groq(api_key=GROQ_API_KEY)