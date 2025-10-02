from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

from sentence_transformers import SentenceTransformer
from schemas.document import DocumentBase
import pymupdf
import os
import re
from transformers import AutoTokenizer

FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/raw/"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 256
OVERLAP = 50

# loading documents from the file path
def load_documents() -> List[DocumentBase]:
  documents: List[DocumentBase] = []
  
  for doc_path in os.listdir(FILE_PATH):
    if doc_path.lower().endswith(".pdf"):
      doc = pymupdf.open(os.path.join(FILE_PATH, doc_path)) # open a document
      content: str = ""
      metadata = doc.metadata
      
      for page in doc: # iterate the document pages
        content += page.get_text()

      documents.append(DocumentBase(content=content, meta=metadata, embedding=[]))  # Placeholder embedding
      doc.close()
  return documents

# cleaning document contents
def clean_document_contents(documents: List[DocumentBase]) -> List[DocumentBase]:
  cleaned_docs: List[DocumentBase] = []
  for doc in documents:
    # Remove extra whitespaces and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters (keep basic punctuation)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    cleaned_docs.append(DocumentBase(content=text, meta=doc.meta, embedding=[]))  # Placeholder embedding

  return cleaned_docs

# chunking and tokenizing
def chunk_documents(documents: List[DocumentBase]):
  tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP
  )

  chunked_docs: List[DocumentBase] = []
  for doc in documents:
    chunks = text_splitter.split_text(doc.content)
    for chunk in chunks:
      chunked_docs.append(DocumentBase(content=chunk, metadata=doc.metadata, embedding=[]))  # Placeholder embedding

  return chunked_docs
  
# embed and store documents
async def embed_documents(documents: List[DocumentBase]) -> List[DocumentBase]:
  model = SentenceTransformer(EMBEDDING_MODEL)
  for doc in documents:
    doc.embedding = model.encode(doc.content).tolist()
  print("Embeddings generated.")
  return documents
