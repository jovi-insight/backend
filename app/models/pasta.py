import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Pasta(Base):
    __tablename__ = "pastas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    id_materia = Column(UUID(as_uuid=True), ForeignKey("materias.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    ultima_atualizacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deletado = Column(Boolean, default=False, nullable=False)
    deletado_em = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    materia = relationship("Materia", back_populates="pastas")
    conteudos = relationship("Conteudo", back_populates="pasta", cascade="all, delete-orphan")
