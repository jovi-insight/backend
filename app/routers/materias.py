# ============================================================
# Router: Matérias
# CRUD de matérias (listar, criar, deletar).
# ============================================================
# Conceitos aplicados:
# - Validação de entrada (duplicidade, existência)
# - Estruturas de decisão (if)
# - Saída de dados com f-string
# - Manipulação de variáveis
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.materia import Materia
from app.schemas.materia import MateriaCreate, MateriaOut

router = APIRouter(prefix="/materias", tags=["Matérias"])


@router.get("", response_model=list[MateriaOut])
async def listar_materias(db: Session = Depends(get_db)):
    """Lista todas as matérias cadastradas ordenadas por nome."""
    # [SAÍDA DE DADOS] Retorna lista de matérias
    return db.query(Materia).order_by(Materia.nome).all()


@router.post("", response_model=MateriaOut, status_code=201)
async def criar_materia(body: MateriaCreate, db: Session = Depends(get_db)):
    """Cria uma nova matéria com validação de duplicidade."""

    # [VALIDAÇÃO] Verifica se o nome está vazio
    if not body.nome.strip():
        raise HTTPException(status_code=400, detail="Nome da matéria não pode ser vazio.")

    # [VALIDAÇÃO + DECISÃO] Verifica se já existe (case-insensitive)
    existente = db.query(Materia).filter(Materia.nome.ilike(body.nome)).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Matéria '{body.nome}' já existe.",  # [F-STRING]
        )

    # [MANIPULAÇÃO DE VARIÁVEIS] Cria e persiste a matéria
    materia = Materia(nome=body.nome.strip())
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia


@router.delete("/{materia_id}", status_code=204)
async def deletar_materia(materia_id: UUID, db: Session = Depends(get_db)):
    """Deleta uma matéria pelo ID."""

    # [VALIDAÇÃO] Verifica se a matéria existe
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(
            status_code=404,
            detail=f"Matéria com ID {materia_id} não encontrada.",  # [F-STRING]
        )

    db.delete(materia)
    db.commit()


@router.put("/{materia_id}", response_model=MateriaOut)
async def atualizar_materia(
    materia_id: UUID,
    body: MateriaCreate,
    db: Session = Depends(get_db),
):
    """Atualiza o nome de uma matéria."""

    # [VALIDAÇÃO] Verifica se o nome está vazio
    if not body.nome.strip():
        raise HTTPException(status_code=400, detail="Nome da matéria não pode ser vazio.")

    # [VALIDAÇÃO] Verifica se a matéria existe
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(
            status_code=404,
            detail=f"Matéria com ID {materia_id} não encontrada.",
        )

    # [VALIDAÇÃO] Verifica duplicidade com outro registro
    existente = (
        db.query(Materia)
        .filter(Materia.nome.ilike(body.nome), Materia.id != materia_id)
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Matéria '{body.nome}' já existe.",
        )

    # [MANIPULAÇÃO DE VARIÁVEIS] Atualiza o nome
    materia.nome = body.nome.strip()
    db.commit()
    db.refresh(materia)
    return materia
