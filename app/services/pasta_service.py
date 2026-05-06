# ============================================================
# Service: Pastas
# Responsável pela lógica de negócio de CRUD de pastas,
# incluindo contagem de arquivos e soft delete.
# ============================================================
# Conceitos aplicados:
# - Manipulação de variáveis tipadas
# - Estruturas de decisão (if/else)
# - Estruturas de repetição (for)
# - Armazenamento e manipulação de listas
# - f-strings em logs
# - Validação de regras de negócio
# ============================================================

from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.pasta import Pasta
from app.models.conteudo import Conteudo


def listar_pastas(db: Session, user_id: str) -> list[dict]:
    """Retorna pastas ativas do usuário com contagem de conteúdos."""

    # [SUBQUERY] Conta conteúdos por pasta (apenas ativos)
    subq = (
        db.query(
            Conteudo.pasta_id,
            func.count(Conteudo.id).label("quantidade_arquivos"),
        )
        .filter(Conteudo.user_id == user_id, Conteudo.deletado == False)
        .group_by(Conteudo.pasta_id)
        .subquery()
    )

    # Busca pastas ativas com a contagem via join
    rows = (
        db.query(Pasta, func.coalesce(subq.c.quantidade_arquivos, 0))
        .outerjoin(subq, Pasta.id == subq.c.pasta_id)
        .filter(Pasta.user_id == user_id, Pasta.deletado == False)
        .order_by(Pasta.ultima_atualizacao.desc())
        .all()
    )

    # [LISTA] Monta lista de resultados
    resultado: list[dict] = []

    # [ESTRUTURA DE REPETIÇÃO - for] Itera sobre cada pasta encontrada
    for pasta, qtd in rows:
        # [LISTA - append] Adiciona pasta formatada ao resultado
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
    """Retorna pasta ativa com seus conteúdos ativos carregados."""
    # [DECISÃO] Filtra apenas pastas não deletadas do usuário
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
    """
    Soft delete da pasta e seus conteúdos filhos.
    Marca registros como deletados sem remover do banco.
    """
    # [VALIDAÇÃO] Verifica se a pasta existe e pertence ao usuário
    pasta = (
        db.query(Pasta)
        .filter(
            Pasta.id == pasta_id,
            Pasta.user_id == user_id,
            Pasta.deletado == False,
        )
        .first()
    )

    # [ESTRUTURA DE DECISÃO - if] Retorna False se não encontrou
    if not pasta:
        return False

    # [MANIPULAÇÃO DE VARIÁVEIS] Captura timestamp atual
    agora: datetime = datetime.now(timezone.utc)

    # [REPETIÇÃO IMPLÍCITA] Atualiza todos os conteúdos filhos em batch
    db.query(Conteudo).filter(
        Conteudo.pasta_id == pasta_id,
        Conteudo.deletado == False,
    ).update({"deletado": True, "deletado_em": agora})

    # [MANIPULAÇÃO DE VARIÁVEIS] Marca a pasta como deletada
    pasta.deletado = True
    pasta.deletado_em = agora

    db.commit()
    return True
