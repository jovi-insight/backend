from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.pasta import PastaOut, PastaDetailOut, PastaUpdate
from app.services import pasta_service
from app.models.pasta import Pasta

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


@router.put("/{pasta_id}", response_model=PastaOut)
async def atualizar_pasta(
    pasta_id: UUID,
    body: PastaUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o nome de uma pasta."""

    # [VALIDAÇÃO] Verifica se o nome está vazio
    if not body.nome.strip():
        raise HTTPException(status_code=400, detail="Nome da pasta não pode ser vazio.")

    # [VALIDAÇÃO] Verifica se a pasta existe e pertence ao usuário
    pasta = (
        db.query(Pasta)
        .filter(Pasta.id == pasta_id, Pasta.user_id == user_id, Pasta.deletado == False)
        .first()
    )
    if not pasta:
        raise HTTPException(status_code=404, detail=f"Pasta com ID {pasta_id} não encontrada.")

    # [MANIPULAÇÃO DE VARIÁVEIS] Atualiza o nome
    pasta.nome = body.nome.strip()
    db.commit()
    db.refresh(pasta)

    # Retorna com quantidade_arquivos = 0 (simplificado no PUT)
    return {
        "id": pasta.id,
        "user_id": pasta.user_id,
        "id_materia": pasta.id_materia,
        "nome": pasta.nome,
        "ultima_atualizacao": pasta.ultima_atualizacao,
        "quantidade_arquivos": 0,
    }
