from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Cria todas as tabelas no banco de dados."""
    from app.models import materia, pasta, conteudo, imagens, audio, termos_chave  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
