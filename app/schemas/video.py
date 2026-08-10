from uuid import UUID
from pydantic import BaseModel


class VideoYoutubeCreate(BaseModel):
    url: str
    titulo: str | None = None


class VideoYoutubeOut(BaseModel):
    id: UUID
    url: str
    titulo: str | None = None

    model_config = {"from_attributes": True}
