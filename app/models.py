"""Modelos de dados (tabelas) da aplicacao."""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """Usuario cadastrado na plataforma."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PDI(SQLModel, table=True):
    """Plano de Desenvolvimento Individual gerado pela IA.

    Guarda tanto os dados que o usuario informou (snapshot do perfil no momento)
    quanto o resultado estruturado devolvido pela IA, em JSON. Isso garante o
    historico de recomendacoes exigido pelo trabalho.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    titulo: str

    # Snapshot do perfil informado pelo usuario
    cargo_atual: str
    nivel_experiencia: str
    area_interesse: str
    objetivo: str
    tecnologias: str
    horas_semanais: int

    # Resultado da IA (JSON serializado como texto)
    conteudo_json: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
