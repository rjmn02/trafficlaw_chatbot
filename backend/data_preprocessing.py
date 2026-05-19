from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from models.document import Document
import pymupdf
import os
import re
from dotenv import load_dotenv
from utils.constants import EMBEDDING_MODEL, hf_client, CHUNK_SIZE, OVERLAP

load_dotenv()

FILE_PATH = os.getenv("DATA_RAW_PATH", "")

# loading documents from the file path
def load_documents() -> List[Document]:
  docs: List[Document] = []

  for name in os.listdir(FILE_PATH):
    if name.lower().endswith(".pdf"):
      path = os.path.join(FILE_PATH, name)
      pdf = pymupdf.open(path)
      content = "".join(page.get_text() for page in pdf)
      pdf.close()
      docs.append(Document(content=content, embedding=[], file_source=name))

  print(f" Loaded {len(docs)} PDF documents.")
  return docs


# cleaning document contents
def clean_document_contents(documents: List[Document]) -> List[Document]:
  cleaned: List[Document] = []
  for d in documents:
    text = d.content
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    text = text.strip()
    cleaned.append(Document(content=text, embedding=[], file_source=d.file_source))
  return cleaned


# chunking and tokenizing
def chunk_documents(documents: List[Document]):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP
  )

  chunked_docs: List[Document] = []
  for doc in documents:
    chunks = text_splitter.split_text(doc.content)
    for chunk in chunks:
      chunked_docs.append(Document(content=chunk, file_source=doc.file_source, embedding=[]))

  return chunked_docs


# embed and store documents
def embed_documents(documents: List[Document]) -> List[Document]:
  if not documents:
    return documents
  texts = [d.content for d in documents]
  embeddings = hf_client.feature_extraction(
    model=EMBEDDING_MODEL,
    text=texts,
    normalize=True  # good for cosine / <-> distance
  )
  for doc, emb in zip(documents, embeddings):
    doc.embedding = emb.tolist()

  # Log embedding completion (using print for script output is acceptable)
  print(f"Embeddings generated for {len(documents)}")
  return documents