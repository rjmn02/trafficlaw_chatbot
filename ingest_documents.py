from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from schemas.document import DocumentBase
import pymupdf
import os
import re
from transformers import AutoTokenizer


FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/raw/"
TOKINIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 256
OVERLAP = 50

def load_documents() -> List[DocumentBase]:
  documents: List[DocumentBase] = []
  
  for doc_path in os.listdir(FILE_PATH):
    if doc_path.lower().endswith(".pdf"):
      doc = pymupdf.open(os.path.join(FILE_PATH, doc_path)) # open a document
      content: str = ""
      metadata = doc.metadata
      
      for page in doc: # iterate the document pages
        content += page.get_text()
        
      documents.append(DocumentBase(content=content, metadata=metadata, embedding=[]))  # Placeholder embedding
      doc.close()

  print(len(documents[0]))
  return documents
  pass

def clean_document_contents(documents: List[DocumentBase]) -> List[DocumentBase]:
  cleaned_docs: List[DocumentBase] = []
  for doc in documents:
    cleaned_content = re.sub(r'\s+', ' ', doc.content).strip()
    cleaned_docs.append(DocumentBase(content=cleaned_content, metadata=doc.metadata, embedding=[]))  # Placeholder embedding

  return cleaned_docs

def chunk_documents(documents: List[DocumentBase], chunk_size=CHUNK_SIZE, overlap=OVERLAP):
  tokenizer = AutoTokenizer.from_pretrained(TOKINIZER_MODEL)
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
    chunk_size=chunk_size,
    chunk_overlap=overlap
  )

  chunked_docs: List[DocumentBase] = []
  for doc in documents:
    chunks = text_splitter.split_text(doc.content)
    for chunk in chunks:
      chunked_docs.append(DocumentBase(content=chunk, metadata=doc.metadata, embedding=[]))  # Placeholder embedding

  return chunked_docs
  

def store_documents(documents: List[DocumentBase]) -> None:
  
  pass

load_documents()