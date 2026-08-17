# ============================================================
# Model: Quiz
# Perguntas de quiz geradas por IA vinculadas a um conteúdo.
# ============================================================

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_conteudo = Column(UUID(as_uuid=True), ForeignKey("conteudos.id"), nullable=False)
    pergunta = Column(Text, nullable=False)
    alternativa_a = Column(String(500), nullable=False)
    alternativa_b = Column(String(500), nullable=False)
    alternativa_c = Column(String(500), nullable=False)
    alternativa_d = Column(String(500), nullable=False)
    resposta_correta = Column(String(1), nullable=False)  # "a", "b", "c" ou "d"
    explicacao = Column(Text, nullable=True)
    criado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    conteudo = relationship("Conteudo", back_populates="quizzes")
