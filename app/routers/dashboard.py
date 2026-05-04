from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.conteudo import ConteudoRecenteOut
from app.services import conteudo_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/recentes", response_model=list[ConteudoRecenteOut])
async def conteudos_recentes(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna os 4 conteúdos mais recentes do usuário."""
    return conteudo_service.listar_recentes(db, user_id, limit=4)
