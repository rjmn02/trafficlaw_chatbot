from pydantic import BaseModel
from typing import List
from schemas.document import DocumentInDB

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    retrieved_docs: List[DocumentInDB]
    memory: List[str]  # conversation history