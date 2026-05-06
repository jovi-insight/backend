# ============================================================
# Router: IA (Inteligência Artificial)
# Endpoints para análise de imagem, tradução e resumo.
# ============================================================
# Conceitos aplicados:
# - Entrada e saída de dados (request/response com f-string)
# - Validação de dados de entrada (tipo de arquivo, existência)
# - Estruturas de decisão (if/elif/else)
# - Manipulação de variáveis tipadas
# - Organização do código em camadas
# ============================================================

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
    """Envia imagem à IA para extração de texto. Salva no cache por 5 min."""

    # [VALIDAÇÃO DE ENTRADA] Verifica se o arquivo é uma imagem válida
    if not imagem.content_type or not imagem.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido: {imagem.content_type}. Envie uma imagem.",
        )

    # [ENTRADA DE DADOS] Lê os bytes da imagem enviada
    image_bytes: bytes = await imagem.read()

    # [MANIPULAÇÃO DE VARIÁVEIS] Chama o serviço de IA
    try:
        resultado: dict = await gemini_service.analisar_imagem(image_bytes, imagem.content_type)
    except Exception as e:
        # [F-STRING] Mensagem de erro formatada
        raise HTTPException(status_code=502, detail=f"Erro ao chamar IA: {e}")

    # [MANIPULAÇÃO DE VARIÁVEIS] Gera ID único para o cache
    cache_id: str = str(uuid_mod.uuid4())
    cache.salvar(cache_id, image_bytes, imagem.content_type)

    # [ESTRUTURA DE DECISÃO - if/else] Busca ou cria matéria sugerida
    materia_sugerida_id = None
    materia_nome: str | None = resultado.get("materia_sugerida")

    if materia_nome:
        # Busca matéria existente (case-insensitive)
        materia = db.query(Materia).filter(Materia.nome.ilike(materia_nome)).first()

        if not materia:
            # [DECISÃO] Se não existe, cria automaticamente
            materia = Materia(nome=materia_nome.strip().title())
            db.add(materia)
            db.commit()
            db.refresh(materia)

        materia_sugerida_id = materia.id

    # [SAÍDA DE DADOS] Retorna resposta estruturada
    return AnalisarImagemResponse(
        texto_extraido=resultado.get("texto_extraido", ""),
        materia_sugerida_id=materia_sugerida_id,
        cache_id=cache_id,
    )


@router.post("/traduzir-imagem", response_model=TraduzirImagemResponse)
async def traduzir_imagem(imagem: UploadFile = File(...)):
    """Envia imagem à IA para tradução do conteúdo visível."""

    # [VALIDAÇÃO DE ENTRADA] Verifica tipo do arquivo
    if not imagem.content_type or not imagem.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido: {imagem.content_type}. Envie uma imagem.",
        )

    # [ENTRADA DE DADOS] Lê bytes da imagem
    image_bytes: bytes = await imagem.read()

    try:
        traducao: str = await gemini_service.traduzir_imagem(image_bytes, imagem.content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao traduzir imagem: {e}")

    # [SAÍDA DE DADOS] Retorna tradução
    return TraduzirImagemResponse(traducao=traducao)


@router.post("/traduzir-texto", response_model=TraduzirTextoResponse)
async def traduzir_texto(body: TraduzirTextoRequest):
    """Recebe texto e retorna tradução para o idioma destino."""

    # [VALIDAÇÃO] Verifica se o texto não está vazio
    if not body.texto.strip():
        raise HTTPException(status_code=400, detail="O texto não pode estar vazio.")

    try:
        traducao: str = await gemini_service.traduzir_texto(body.texto, body.idioma_destino)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao traduzir texto: {e}")

    # [SAÍDA - f-string implícita no JSON de resposta]
    return TraduzirTextoResponse(traducao=traducao)


@router.post("/resumo", response_model=ResumoResponse)
async def gerar_resumo(
    body: ResumoRequest,
    db: Session = Depends(get_db),
):
    """Gera resumo por IA com base no conteúdo salvo no banco."""

    # [VALIDAÇÃO] Verifica se o conteúdo existe
    conteudo = db.query(Conteudo).filter(Conteudo.id == body.conteudo_id).first()

    if not conteudo:
        raise HTTPException(
            status_code=404,
            detail=f"Conteúdo com ID {body.conteudo_id} não encontrado.",
        )

    # [VALIDAÇÃO] Verifica se há texto para resumir
    if not conteudo.extracao_original:
        raise HTTPException(
            status_code=400,
            detail="Conteúdo não possui texto para resumir.",
        )

    try:
        resumo: str = await gemini_service.gerar_resumo(conteudo.extracao_original)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao gerar resumo: {e}")

    # [MANIPULAÇÃO DE VARIÁVEIS] Salva o resumo no banco
    conteudo.resumo_ia = resumo
    db.commit()

    return ResumoResponse(resumo=resumo)
