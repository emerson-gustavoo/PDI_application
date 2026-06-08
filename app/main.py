"""Ponto de entrada da aplicacao FastAPI - Mentor PDI."""
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session
from pathlib import Path

from .config import settings
from .database import init_db, get_session
from .templating import templates
from .routers import auth_routes, pdi_routes
from .routers.pdi_routes import _get_user

app = FastAPI(title="Mentor PDI", description="Mentor de carreira em TI com IA")

# Sessao baseada em cookie assinado (guarda o id do usuario logado)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Arquivos estaticos (CSS)
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Rotas
app.include_router(auth_routes.router)
app.include_router(pdi_routes.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    user = _get_user(request, session)
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})
