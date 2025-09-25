from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from schemas.document import DocumentBase
import pymupdf
import os
from transformers import AutoTokenizer


FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/raw/"
CHUNK_SIZE = 256
OVERLAP = 50

def load_documents():
  documents: List[DocumentBase] = []
  
  for doc_path in os.listdir(FILE_PATH):
    if doc_path.lower().endswith(".pdf"):
      doc = pymupdf.open(os.path.join(FILE_PATH, doc_path)) # open a document
      content: str = ""
      metadata = doc.metadata
      
      for page in doc: # iterate the document pages
        content += page.get_text()
        
      documents.append({"content": content, "metadata": metadata})
      doc.close()

  print(len(documents[0]))
  return documents
  pass

def clean_texts(documents: List[DocumentBase]):
  
  pass

def chunk_documents(documents: DocumentBase, chunk_size=500, overlap=50):
  tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
  
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
    chunk_size=256,
    chunk_overlap=50
  )
  
  text_chunks = text_splitter.split_documents(documents=documents)
  return text_chunks

def store_documents(chunks):
  pass

load_documents()