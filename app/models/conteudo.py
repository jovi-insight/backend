import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Conteudo(Base):
    __tablename__ = "conteudos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    pasta_id = Column(UUID(as_uuid=True), ForeignKey("pastas.id"), nullable=False)
    extracao_original = Column(Text, nullable=True)
    resumo_ia = Column(Text, nullable=True)
    ultima_atualizacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deletado = Column(Boolean, default=False, nullable=False)
    deletado_em = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    pasta = relationship("Pasta", back_populates="conteudos")
    imagens = relationship("Imagem", back_populates="conteudo", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="conteudo", cascade="all, delete-orphan")
    termos_chave = relationship("TermoChave", back_populates="conteudo", cascade="all, delete-orphan")
