from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core import cache
from app.schemas.conteudo import ConteudoOut, ConteudoConfirmarRequest
from app.models.materia import Materia
from app.models.conteudo import Conteudo
from app.services import storage_service, conteudo_service, gemini_service

router = APIRouter(prefix="/conteudo", tags=["Conteúdo"])


@router.get("/{conteudo_id}", response_model=ConteudoOut)
async def obter_conteudo(
    conteudo_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna um conteúdo com imagens e vídeos recomendados."""
    conteudo = (
        db.query(Conteudo)
        .options(
            joinedload(Conteudo.imagens),
            joinedload(Conteudo.videos),
        )
        .filter(
            Conteudo.id == conteudo_id,
            Conteudo.user_id == user_id,
            Conteudo.deletado == False,
        )
        .first()
    )
    if not conteudo:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado.")
    return conteudo


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
    3. Pede à IA recomendações de vídeos do YouTube
    4. Cria Pasta (se necessário), Conteudo, Imagem e Vídeos no banco
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

    # Pede à IA recomendações de vídeos do YouTube
    try:
        videos = await gemini_service.recomendar_videos(body.texto_extraido, materia.nome)
        print(f"🎬 Vídeos recomendados: {videos}")
    except Exception as e:
        import traceback
        print(f"⚠️  Erro ao buscar vídeos: {e}")
        traceback.print_exc()
        videos = []  # Se falhar, salva sem vídeos

    conteudo = conteudo_service.criar_conteudo_com_imagem(
        db=db,
        user_id=user_id,
        id_materia=body.id_materia,
        texto_extraido=body.texto_extraido,
        url_imagem=url_imagem,
        videos=videos,
    )
    return conteudo
