from pydantic import BaseModel, Field, field_validator
from typing import List
from schemas.document import DocumentInDB

class QueryRequest(BaseModel):
  session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
  query: str = Field(..., min_length=1, max_length=5000, description="User query")
  
  @field_validator('query')
  @classmethod
  def validate_query(cls, v: str) -> str:
    cleaned = v.strip()
    if len(cleaned) == 0:
      raise ValueError('Query cannot be empty')
    if len(cleaned) > 5000:
      raise ValueError('Query exceeds maximum length of 5000 characters')
    return cleaned
  
  @field_validator('session_id')
  @classmethod
  def validate_session_id(cls, v: str) -> str:
    if len(v) == 0:
      raise ValueError('Session ID cannot be empty')
    if len(v) > 100:
      raise ValueError('Session ID exceeds maximum length of 100 characters')
    # Allow UUIDs, alphanumeric, hyphens, underscores, dots
    if not all(c.isalnum() or c in '-_.' for c in v):
      raise ValueError('Session ID contains invalid characters')
    return v

class QueryResponse(BaseModel):
  answer: str
  retrieved_docs: List[str]

class ClearSessionResponse(BaseModel):
  cleared: bool
  message: str