from pydantic import BaseModel
from typing import List
from schemas.document import DocumentInDB

class QueryRequest(BaseModel):
  query: str
  # session_id: str # Add session_id

class QueryResponse(BaseModel):
  answer: str
  retrieved_docs: List[str]