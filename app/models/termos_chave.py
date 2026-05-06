import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TermoChave(Base):
    __tablename__ = "termos_chave"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_conteudo = Column(UUID(as_uuid=True), ForeignKey("conteudos.id"), nullable=False)
    termo = Column(String(255), nullable=False)

    # Relationships
    conteudo = relationship("Conteudo", back_populates="termos_chave")
