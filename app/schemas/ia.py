from uuid import UUID
from pydantic import BaseModel


class AnalisarImagemResponse(BaseModel):
    texto_extraido: str
    materia_sugerida_id: UUID | None = None
    cache_id: str


class TraduzirImagemResponse(BaseModel):
    traducao: str


class TraduzirTextoRequest(BaseModel):
    texto: str
    idioma_destino: str = "português brasileiro"


class TraduzirTextoResponse(BaseModel):
    traducao: str


class ResumoRequest(BaseModel):
    conteudo_id: UUID


class ResumoResponse(BaseModel):
    resumo: str
