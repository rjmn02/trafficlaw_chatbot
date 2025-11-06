from sqlalchemy import String, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import datetime
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class Document(Base):
  __tablename__ = 'document'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  content: Mapped[str] = mapped_column(Text, nullable=False)
  embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False) # all-MiniLM embeds 384-dims
  file_source: Mapped[str] = mapped_column(String, nullable=True)
  created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
  updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
  