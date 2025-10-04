from langchain_community.document_loaders import PyMuPDFLoader
from embedding_model import get_embedding_model
from vector_store import get_vector_store
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from typing import List
import os
import re

FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/raw/"


# Text cleaning function
def clean_text(text: str) -> str:
  # Remove extra whitespaces and newlines
  text = re.sub(r'\s+', ' ', text)
  
  # Remove non-printable characters (keep basic punctuation)
  text = re.sub(r'[^\x20-\x7E\n]', '', text)
  
  # Strip leading/trailing whitespace
  text = text.strip()
  return text

# load documents
def load_documents(path: str) -> List[Document]:
  documents = []
  pdf_count = 0
  
  for filename in os.listdir(path):
    if filename.lower().endswith(".pdf"):
      pdf_count += 1
      try:
        loader = PyMuPDFLoader(os.path.join(path, filename))
        documents_raw = loader.load()
        # clean text in each document
        for doc in documents_raw:
          doc.page_content = clean_text(doc.page_content)
        documents.extend(documents_raw)
      except Exception as e:
        print(f"Error loading {filename}: {e}")
      
  print(len(documents), "documents loaded.")
  print(f"{pdf_count} PDFs processed.")
  
  return documents

# chunking and tokenizing
def text_chunking(
  documents: List[Document], 
) -> List[Document]:
  tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
    chunk_size=256,
    chunk_overlap=50
  )

  text_chunks = text_splitter.split_documents(documents=documents)
  return text_chunks

def store_in_db(
  text_chunks: List[Document],
) -> None:
  embedding_model = get_embedding_model()
  vector_store = get_vector_store(
    embeddings=embedding_model,
    collection_name="trafficlaw_docs",
  )

  vector_store.add_documents(documents=text_chunks)


  


def main():
  documents = load_documents(FILE_PATH)
  if not documents:
    print("No documents found.")
    return

  text_chunks = text_chunking(documents=documents)
  store_in_db(text_chunks=text_chunks)
  print("Data preprocessing and storage complete.")