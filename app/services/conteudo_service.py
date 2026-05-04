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
    # Busca ou cria a pasta (usa nome da matéria como nome da pasta)
    pasta = (
        db.query(Pasta)
        .filter(Pasta.user_id == user_id, Pasta.id_materia == id_materia, Pasta.deletado == False)
        .first()
    )
    if not pasta:
        materia = db.query(Materia).filter(Materia.id == id_materia).first()
        nome_pasta = materia.nome if materia else "Nova Pasta"
        pasta = Pasta(
            user_id=user_id,
            id_materia=id_materia,
            nome=nome_pasta,
        )
        db.add(pasta)
        db.flush()

    conteudo = Conteudo(
        user_id=user_id,
        pasta_id=pasta.id,
        extracao_original=texto_extraido,
    )
    db.add(conteudo)
    db.flush()

    imagem = Imagem(id_conteudo=conteudo.id, url_storage=url_imagem)
    db.add(imagem)

    db.commit()
    db.refresh(conteudo)
    return conteudo


def listar_recentes(db: Session, user_id: str, limit: int = 4) -> list[dict]:
    """Retorna os N conteúdos mais recentes do usuário com URL da primeira imagem."""
    conteudos = (
        db.query(Conteudo)
        .options(joinedload(Conteudo.imagens))
        .filter(Conteudo.user_id == user_id, Conteudo.deletado == False)
        .order_by(Conteudo.ultima_atualizacao.desc())
        .limit(limit)
        .all()
    )
    resultado = []
    for c in conteudos:
        resultado.append(
            {
                "id": c.id,
                "pasta_id": c.pasta_id,
                "extracao_original": c.extracao_original,
                "resumo_ia": c.resumo_ia,
                "ultima_atualizacao": c.ultima_atualizacao,
                "imagem_url": c.imagens[0].url_storage if c.imagens else None,
            }
        )
    return resultado
