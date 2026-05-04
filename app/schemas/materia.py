from uuid import UUID
from pydantic import BaseModel


class MateriaBase(BaseModel):
    nome: str


class MateriaCreate(MateriaBase):
    pass


class MateriaOut(MateriaBase):
    id: UUID

    model_config = {"from_attributes": True}
