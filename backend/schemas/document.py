from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
  content: str
  embedding: list[float]
  meta: dict

class DocumentInDB(DocumentBase):
  id: int
  file_source: str | None = None  # Add this field
  created_at: datetime
  updated_at: datetime
  
  model_config = {
    "from_attributes": True
  }