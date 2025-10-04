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

# loading documents from the file path
def load_documents() -> List[Document]:
    docs: List[Document] = []
    count = 0
    for name in os.listdir(FILE_PATH):
      if name.lower().endswith(".pdf"):
        count += 1
        path = os.path.join(FILE_PATH, name)
        pdf = pymupdf.open(path)
        content = "".join(page.get_text() for page in pdf)
        pdf.close()
        docs.append(Document(content=content, embedding=[], file_source=name))
    print(f"Loaded {count} documents.")
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
  tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
  text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
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
  model = SentenceTransformer(EMBEDDING_MODEL)
  for doc in documents:
    doc.embedding = model.encode(doc.content).tolist()
  print("Embeddings generated.")
  return documents
