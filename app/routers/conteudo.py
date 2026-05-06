from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core import cache
from app.schemas.conteudo import ConteudoOut, ConteudoConfirmarRequest
from app.models.materia import Materia
from app.services import storage_service, conteudo_service

router = APIRouter(prefix="/conteudo", tags=["Conteúdo"])


@router.post("/confirmar", response_model=ConteudoOut)
async def confirmar_conteudo(
    body: ConteudoConfirmarRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirma conteúdo analisado:
    1. Recupera imagem do cache (enviada no /analisar-imagem)
    2. Upload pro Supabase Storage
    3. Cria Pasta (se necessário), Conteudo e Imagem no banco
    """
    # Recupera imagem do cache
    entry = cache.obter(body.cache_id)
    if entry is None:
        raise HTTPException(
            status_code=410,
            detail="Imagem expirou do cache (limite: 5 min). Envie novamente via /ia/analisar-imagem.",
        )

    materia = db.query(Materia).filter(Materia.id == body.id_materia).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria não encontrada.")

    # Upload pro Supabase
    try:
        url_imagem = await storage_service.upload_image(
            entry.file_bytes, entry.content_type, materia.nome
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro no upload: {e}")

    # Remove do cache após upload bem-sucedido
    cache.remover(body.cache_id)

    conteudo = conteudo_service.criar_conteudo_com_imagem(
        db=db,
        user_id=user_id,
        id_materia=body.id_materia,
        texto_extraido=body.texto_extraido,
        url_imagem=url_imagem,
    )
    return conteudo
