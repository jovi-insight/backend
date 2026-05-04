from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.pasta import Pasta
from app.models.conteudo import Conteudo


def listar_pastas(db: Session, user_id: str) -> list[dict]:
    """Retorna pastas ativas do usuário com contagem de conteúdos."""
    subq = (
        db.query(
            Conteudo.pasta_id,
            func.count(Conteudo.id).label("quantidade_arquivos"),
        )
        .filter(Conteudo.user_id == user_id, Conteudo.deletado == False)
        .group_by(Conteudo.pasta_id)
        .subquery()
    )

    rows = (
        db.query(Pasta, func.coalesce(subq.c.quantidade_arquivos, 0))
        .outerjoin(subq, Pasta.id == subq.c.pasta_id)
        .filter(Pasta.user_id == user_id, Pasta.deletado == False)
        .order_by(Pasta.ultima_atualizacao.desc())
        .all()
    )

    resultado = []
    for pasta, qtd in rows:
        resultado.append(
            {
                "id": pasta.id,
                "user_id": pasta.user_id,
                "id_materia": pasta.id_materia,
                "nome": pasta.nome,
                "ultima_atualizacao": pasta.ultima_atualizacao,
                "quantidade_arquivos": qtd,
            }
        )
    return resultado


def obter_pasta(db: Session, pasta_id: UUID, user_id: str) -> Pasta | None:
    """Retorna pasta ativa com seus conteúdos ativos."""
    return (
        db.query(Pasta)
        .options(joinedload(Pasta.conteudos).joinedload(Conteudo.imagens))
        .filter(
            Pasta.id == pasta_id,
            Pasta.user_id == user_id,
            Pasta.deletado == False,
        )
        .first()
    )


def deletar_pasta(db: Session, pasta_id: UUID, user_id: str) -> bool:
    """Soft delete da pasta e seus conteúdos."""
    pasta = (
        db.query(Pasta)
        .filter(
            Pasta.id == pasta_id,
            Pasta.user_id == user_id,
            Pasta.deletado == False,
        )
        .first()
    )
    if not pasta:
        return False

    agora = datetime.now(timezone.utc)

    # Soft delete dos conteúdos filhos
    db.query(Conteudo).filter(
        Conteudo.pasta_id == pasta_id,
        Conteudo.deletado == False,
    ).update({"deletado": True, "deletado_em": agora})

    # Soft delete da pasta
    pasta.deletado = True
    pasta.deletado_em = agora

    db.commit()
    return True
