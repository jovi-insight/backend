from sqlalchemy.orm import Session
from app.models.materia import Materia

MATERIAS_BASE = [
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
    if db.query(Materia).first() is not None:
        return
    for nome in MATERIAS_BASE:
        db.add(Materia(nome=nome))
    db.commit()
