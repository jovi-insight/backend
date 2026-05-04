from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.materia import Materia
from app.schemas.materia import MateriaCreate, MateriaOut

router = APIRouter(prefix="/materias", tags=["Matérias"])


@router.get("", response_model=list[MateriaOut])
async def listar_materias(db: Session = Depends(get_db)):
    """Lista todas as matérias cadastradas."""
    return db.query(Materia).order_by(Materia.nome).all()


@router.post("", response_model=MateriaOut, status_code=201)
async def criar_materia(body: MateriaCreate, db: Session = Depends(get_db)):
    """Cria uma nova matéria."""
    existente = db.query(Materia).filter(Materia.nome.ilike(body.nome)).first()
    if existente:
        raise HTTPException(status_code=409, detail="Matéria já existe.")
    materia = Materia(nome=body.nome)
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia


@router.delete("/{materia_id}", status_code=204)
async def deletar_materia(materia_id: UUID, db: Session = Depends(get_db)):
    """Deleta uma matéria."""
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria não encontrada.")
    db.delete(materia)
    db.commit()
