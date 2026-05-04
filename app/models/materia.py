import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Materia(Base):
    __tablename__ = "materias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), unique=True, nullable=False)

    # Relationships
    pastas = relationship("Pasta", back_populates="materia", cascade="all, delete-orphan")
