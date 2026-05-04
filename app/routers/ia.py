from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid as uuid_mod

from app.schemas.ia import (
    AnalisarImagemResponse,
    TraduzirImagemResponse,
    TraduzirTextoRequest,
    TraduzirTextoResponse,
    ResumoRequest,
    ResumoResponse,
)
from app.services import gemini_service
from app.models.materia import Materia
from app.models.conteudo import Conteudo
from app.core.database import get_db
from app.core import cache

router = APIRouter(prefix="/ia", tags=["IA"])


@router.post("/analisar-imagem", response_model=AnalisarImagemResponse)
async def analisar_imagem(
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Envia imagem ao Gemini para extração de texto. Não salva no banco."""
    if not imagem.content_type or not imagem.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem.")

    image_bytes = await imagem.read()
    try:
        resultado = await gemini_service.analisar_imagem(image_bytes, imagem.content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao chamar Gemini: {e}")

    # Salva imagem no cache (expira em 5 min)
    cache_id = str(uuid_mod.uuid4())
    cache.salvar(cache_id, image_bytes, imagem.content_type)

    # Tenta encontrar a matéria sugerida pelo nome, ou cria se não existir
    materia_sugerida_id = None
    materia_nome = resultado.get("materia_sugerida")
    if materia_nome:
        materia = db.query(Materia).filter(Materia.nome.ilike(materia_nome)).first()
        if not materia:
            materia = Materia(nome=materia_nome.strip().title())
            db.add(materia)
            db.commit()
            db.refresh(materia)
        materia_sugerida_id = materia.id

    return AnalisarImagemResponse(
        texto_extraido=resultado.get("texto_extraido", ""),
        materia_sugerida_id=materia_sugerida_id,
        cache_id=cache_id,
    )


@router.post("/traduzir-imagem", response_model=TraduzirImagemResponse)
async def traduzir_imagem(imagem: UploadFile = File(...)):
    """Envia imagem ao Gemini para tradução do conteúdo."""
    if not imagem.content_type or not imagem.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem.")

    image_bytes = await imagem.read()
    try:
        traducao = await gemini_service.traduzir_imagem(image_bytes, imagem.content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao chamar Gemini: {e}")

    return TraduzirImagemResponse(traducao=traducao)


@router.post("/traduzir-texto", response_model=TraduzirTextoResponse)
async def traduzir_texto(body: TraduzirTextoRequest):
    """Recebe um texto e retorna a tradução via Gemini."""
    try:
        traducao = await gemini_service.traduzir_texto(body.texto, body.idioma_destino)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao chamar Gemini: {e}")

    return TraduzirTextoResponse(traducao=traducao)


@router.post("/resumo", response_model=ResumoResponse)
async def gerar_resumo(
    body: ResumoRequest,
    db: Session = Depends(get_db),
):
    """Gera um resumo por IA com base no conteúdo salvo no banco."""
    conteudo = db.query(Conteudo).filter(Conteudo.id == body.conteudo_id).first()
    if not conteudo:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado.")
    if not conteudo.extracao_original:
        raise HTTPException(status_code=400, detail="Conteúdo não possui texto para resumir.")

    try:
        resumo = await gemini_service.gerar_resumo(conteudo.extracao_original)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao gerar resumo: {e}")

    # Salva o resumo no banco
    conteudo.resumo_ia = resumo
    db.commit()

    return ResumoResponse(resumo=resumo)
