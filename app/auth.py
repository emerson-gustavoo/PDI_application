"""Autenticacao: hash de senha e helpers de sessao."""
import bcrypt
from fastapi import Request


def hash_password(password: str) -> str:
    # bcrypt aceita no maximo 72 bytes; truncamos por seguranca
    pw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))


def login_user(request: Request, user_id: int) -> None:
    """Grava o id do usuario na sessao (cookie assinado)."""
    request.session["user_id"] = user_id


def logout_user(request: Request) -> None:
    request.session.clear()


def current_user_id(request: Request):
    """Retorna o id do usuario logado, ou None."""
    return request.session.get("user_id")
