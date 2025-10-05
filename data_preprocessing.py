from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from models.document import Document
from sentence_transformers import SentenceTransformer
import pymupdf
import os
import re
from transformers import AutoTokenizer

FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/raw/"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 256
OVERLAP = 50
EMBED_BATCH_SIZE = 64
EMBED_DEVICE = "cpu"  # "cpu" or "cuda"

_tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
_embedder = SentenceTransformer(EMBEDDING_MODEL, device=EMBED_DEVICE)

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
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = text.strip()
    cleaned.append(Document(content=text, embedding=[], file_source=d.file_source))
  return cleaned


# chunking and tokenizing
def chunk_documents(documents: List[Document]):
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=_tokenizer,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP
  )

  chunked_docs: List[Document] = []
  for doc in documents:
    chunks = text_splitter.split_text(doc.content)
    for chunk in chunks:
      chunked_docs.append(Document(content=chunk, file_source=doc.file_source, embedding=[]))  # Placeholder embedding

  return chunked_docs
  
# embed and store documents
async def embed_documents(documents: List[Document]) -> List[Document]:

  if not documents:
    return documents
  texts = [d.content for d in documents]
  embeddings = _embedder.encode(
    texts,
    batch_size=EMBED_BATCH_SIZE,
    show_progress_bar=True,
    normalize_embeddings=True  # good for cosine / <-> distance
  )
  for doc, emb in zip(documents, embeddings):
    doc.embedding = emb.tolist()
    
  print(f"Embeddings generated for {len(documents)} chunks (batch size={EMBED_BATCH_SIZE}).")
  return documents
