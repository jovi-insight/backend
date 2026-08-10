from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.schemas.imagem import ImagemOut
from app.schemas.video import VideoYoutubeCreate, VideoYoutubeOut


class ConteudoConfirmarRequest(BaseModel):
    cache_id: str
    id_materia: UUID
    texto_extraido: str


class ConteudoOut(BaseModel):
    id: UUID
    user_id: str
    pasta_id: UUID
    extracao_original: str | None = None
    resumo_ia: str | None = None
    ultima_atualizacao: datetime | None = None
    imagens: list[ImagemOut] = []
    videos: list[VideoYoutubeOut] = []

    model_config = {"from_attributes": True}


class ConteudoRecenteOut(BaseModel):
    id: UUID
    pasta_id: UUID
    extracao_original: str | None = None
    resumo_ia: str | None = None
    ultima_atualizacao: datetime | None = None
    imagem_url: str | None = None

    model_config = {"from_attributes": True}
