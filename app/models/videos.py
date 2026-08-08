import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VideoYoutube(Base):
    __tablename__ = "videos_youtube"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_conteudo = Column(UUID(as_uuid=True), ForeignKey("conteudos.id"), nullable=False)
    url = Column(String(500), nullable=False)
    titulo = Column(String(300), nullable=True)
    ultima_atualizacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    conteudo = relationship("Conteudo", back_populates="videos")
