from pydantic import BaseModel
from typing import List
from schemas.document import DocumentInDB

class QueryRequest(BaseModel):
  session_id: str
  query: str

class QueryResponse(BaseModel):
  answer: str
  retrieved_docs: List[str]