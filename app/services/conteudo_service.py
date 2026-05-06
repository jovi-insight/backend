# ============================================================
# Service: Conteúdo
# Responsável pela lógica de negócio de criação e listagem
# de conteúdos do usuário.
# ============================================================
# Conceitos aplicados:
# - Manipulação de variáveis (tipadas com Type Hints)
# - Estruturas de decisão (if/else)
# - Estruturas de repetição (for)
# - Armazenamento e manipulação de dados com listas
# - f-strings (logs e mensagens)
# - Validação de dados de entrada
# - Organização em camadas (service separado do router)
# ============================================================

from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.models.pasta import Pasta
from app.models.conteudo import Conteudo
from app.models.imagens import Imagem
from app.models.materia import Materia


def criar_conteudo_com_imagem(
    db: Session,
    user_id: str,
    id_materia: UUID,
    texto_extraido: str,
    url_imagem: str,
) -> Conteudo:
    """
    Cria pasta (se não existir), conteúdo e vincula a imagem.
    Chamado APÓS o upload no Storage ter sucesso.
    """
    # [ESTRUTURA DE DECISÃO] Verifica se já existe pasta ativa para a matéria
    pasta = (
        db.query(Pasta)
        .filter(Pasta.user_id == user_id, Pasta.id_materia == id_materia, Pasta.deletado == False)
        .first()
    )

    if not pasta:
        # [MANIPULAÇÃO DE VARIÁVEIS] Busca nome da matéria para usar como nome da pasta
        materia = db.query(Materia).filter(Materia.id == id_materia).first()
        nome_pasta: str = materia.nome if materia else "Nova Pasta"

        # [DECISÃO] Cria nova pasta apenas se não existir
        pasta = Pasta(
            user_id=user_id,
            id_materia=id_materia,
            nome=nome_pasta,
        )
        db.add(pasta)
        db.flush()  # Gera o ID sem commitar

    # [MANIPULAÇÃO DE VARIÁVEIS] Cria o conteúdo vinculado à pasta
    conteudo = Conteudo(
        user_id=user_id,
        pasta_id=pasta.id,
        extracao_original=texto_extraido,
    )
    db.add(conteudo)
    db.flush()

    # [MANIPULAÇÃO DE VARIÁVEIS] Vincula a imagem ao conteúdo
    imagem = Imagem(id_conteudo=conteudo.id, url_storage=url_imagem)
    db.add(imagem)

    db.commit()
    db.refresh(conteudo)
    return conteudo


def listar_recentes(db: Session, user_id: str, limit: int = 4) -> list[dict]:
    """
    Retorna os N conteúdos mais recentes do usuário.
    Inclui a URL da primeira imagem vinculada.
    """
    # [VALIDAÇÃO] Garante que limit é positivo
    if limit <= 0:
        limit = 4

    # Busca conteúdos ativos com imagens carregadas (eager loading)
    conteudos = (
        db.query(Conteudo)
        .options(joinedload(Conteudo.imagens))
        .filter(Conteudo.user_id == user_id, Conteudo.deletado == False)
        .order_by(Conteudo.ultima_atualizacao.desc())
        .limit(limit)
        .all()
    )

    # [LISTA] Monta lista de resultados usando repetição
    resultado: list[dict] = []

    # [ESTRUTURA DE REPETIÇÃO - for] Itera sobre cada conteúdo encontrado
    for c in conteudos:
        # [DECISÃO - if/else] Verifica se existe imagem vinculada
        if c.imagens:
            imagem_url = c.imagens[0].url_storage
        else:
            imagem_url = None

        # [LISTA - append] Adiciona item formatado à lista de resultados
        resultado.append(
            {
                "id": c.id,
                "pasta_id": c.pasta_id,
                "extracao_original": c.extracao_original,
                "resumo_ia": c.resumo_ia,
                "ultima_atualizacao": c.ultima_atualizacao,
                "imagem_url": imagem_url,
            }
        )

    return resultado
