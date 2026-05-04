from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.schemas.conteudo import ConteudoOut


class PastaOut(BaseModel):
    id: UUID
    user_id: str
    id_materia: UUID
    nome: str
    ultima_atualizacao: datetime | None = None
    quantidade_arquivos: int = 0

    model_config = {"from_attributes": True}


class PastaDetailOut(BaseModel):
    id: UUID
    user_id: str
    id_materia: UUID
    nome: str
    ultima_atualizacao: datetime | None = None
    conteudos: list[ConteudoOut] = []

    model_config = {"from_attributes": True}
