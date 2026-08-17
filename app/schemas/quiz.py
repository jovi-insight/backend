from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class QuizOut(BaseModel):
    id: UUID
    id_conteudo: UUID
    pergunta: str
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    resposta_correta: str
    explicacao: str | None = None
    criado_em: datetime | None = None

    model_config = {"from_attributes": True}


class GerarQuizRequest(BaseModel):
    conteudo_id: UUID
    num_perguntas: int = 5


class GerarQuizResponse(BaseModel):
    conteudo_id: UUID
    perguntas: list[QuizOut]
