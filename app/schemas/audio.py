from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class AudioOut(BaseModel):
    id: UUID
    id_conteudo: UUID
    url_storage: str
    ultima_atualizacao: datetime | None = None

    model_config = {"from_attributes": True}
