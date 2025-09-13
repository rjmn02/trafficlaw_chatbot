from langchain_postgres import PGVector
import os

from dotenv import load_dotenv

load_dotenv()

def get_vector_store(
  embeddings,
  collection_name: str = "documents",
  connection: str = None
) -> PGVector:

  if connection is None:
      connection = os.getenv("DATABASE_URL")
  return PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection
  )