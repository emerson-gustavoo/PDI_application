"""Conexao e sessao do banco de dados usando SQLModel."""
from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# connect_args so e necessario para SQLite (permite uso entre threads do uvicorn)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Cria as tabelas se ainda nao existirem."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency do FastAPI: entrega uma sessao por requisicao."""
    with Session(engine) as session:
        yield session
