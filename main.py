from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from ingest_documents import load_documents, text_chunking
from embedding_model import get_embedding_model
from vector_store import get_vector_store

app = FastAPI()



  
  
  