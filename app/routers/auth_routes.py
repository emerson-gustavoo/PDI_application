"""Rotas de cadastro, login e logout."""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..auth import hash_password, verify_password, login_user, logout_user
from ..templating import templates

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    # Verifica duplicidade
    existing = session.exec(
        select(User).where((User.username == username) | (User.email == email))
    ).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "erro": "Usuario ou e-mail ja cadastrado."},
            status_code=400,
        )

    user = User(username=username, email=email, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    login_user(request, user.id)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Usuario ou senha invalidos."},
            status_code=401,
        )

    login_user(request, user.id)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/", status_code=303)
