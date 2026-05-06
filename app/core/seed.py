# ============================================================
# Seed: Matérias Base
# Popula o banco com matérias padrão no primeiro startup.
# ============================================================
# Conceitos aplicados:
# - Armazenamento com listas
# - Estruturas de repetição (for)
# - Estruturas de decisão (if)
# - Manipulação de variáveis
# ============================================================

from sqlalchemy.orm import Session
from app.models.materia import Materia

# [LISTA] Matérias base pré-cadastradas
MATERIAS_BASE: list[str] = [
    "Matemática",
    "Física",
    "Química",
    "Biologia",
    "História",
    "Geografia",
    "Português",
    "Inglês",
    "Espanhol",
    "Filosofia",
    "Sociologia",
    "Literatura",
    "Educação Física",
    "Artes",
    "Programação",
    "Banco de Dados",
    "Redes de Computadores",
    "Engenharia de Software",
    "Inteligência Artificial",
    "Cálculo",
    "Álgebra Linear",
    "Estatística",
    "Direito",
    "Economia",
    "Administração",
    "Contabilidade",
]


def seed_materias(db: Session) -> None:
    """Insere matérias base se a tabela estiver vazia."""

    # [DECISÃO - if] Só insere se não houver nenhuma matéria cadastrada
    if db.query(Materia).first() is not None:
        return

    # [REPETIÇÃO - for] Itera sobre a lista de matérias
    for nome in MATERIAS_BASE:
        # [MANIPULAÇÃO DE VARIÁVEIS] Cria instância do model
        nova_materia = Materia(nome=nome)
        db.add(nova_materia)

    db.commit()
