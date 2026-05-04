from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.pasta import PastaOut, PastaDetailOut
from app.services import pasta_service

router = APIRouter(prefix="/pastas", tags=["Pastas"])


@router.get("", response_model=list[PastaOut])
async def listar_pastas(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista pastas do usuário com contagem de arquivos."""
    return pasta_service.listar_pastas(db, user_id)


@router.get("/{pasta_id}", response_model=PastaDetailOut)
async def obter_pasta(
    pasta_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna pasta com seus conteúdos e imagens."""
    pasta = pasta_service.obter_pasta(db, pasta_id, user_id)
    if not pasta:
        raise HTTPException(status_code=404, detail="Pasta não encontrada.")
    return pasta


@router.delete("/{pasta_id}", status_code=204)
async def deletar_pasta(
    pasta_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete da pasta e seus conteúdos. Imagens permanecem no Storage."""
    deleted = pasta_service.deletar_pasta(db, pasta_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pasta não encontrada.")
