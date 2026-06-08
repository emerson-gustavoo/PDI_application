"""Rotas do PDI: painel, geracao e visualizacao."""
import json

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..models import User, PDI
from ..auth import current_user_id
from ..templating import templates
from ..ai_service import generate_pdi

router = APIRouter()


def _get_user(request: Request, session: Session):
    """Retorna o User logado ou None."""
    uid = current_user_id(request)
    if uid is None:
        return None
    return session.get(User, uid)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    user = _get_user(request, session)
    if not user:
        return RedirectResponse("/login", status_code=303)

    pdis = session.exec(
        select(PDI).where(PDI.user_id == user.id).order_by(PDI.created_at.desc())
    ).all()
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user, "pdis": pdis}
    )


@router.get("/pdi/novo", response_class=HTMLResponse)
def novo_pdi_form(request: Request, session: Session = Depends(get_session)):
    user = _get_user(request, session)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("new_pdi.html", {"request": request, "user": user})


@router.post("/pdi/novo")
def criar_pdi(
    request: Request,
    cargo_atual: str = Form(...),
    nivel_experiencia: str = Form(...),
    area_interesse: str = Form(...),
    objetivo: str = Form(...),
    tecnologias: str = Form(...),
    horas_semanais: int = Form(...),
    session: Session = Depends(get_session),
):
    user = _get_user(request, session)
    if not user:
        return RedirectResponse("/login", status_code=303)

    dados = {
        "cargo_atual": cargo_atual,
        "nivel_experiencia": nivel_experiencia,
        "area_interesse": area_interesse,
        "objetivo": objetivo,
        "tecnologias": tecnologias,
        "horas_semanais": horas_semanais,
    }

    try:
        resultado = generate_pdi(dados)
    except Exception as exc:  # erro de API, JSON invalido, etc.
        return templates.TemplateResponse(
            "new_pdi.html",
            {
                "request": request,
                "user": user,
                "erro": f"Falha ao gerar o PDI: {exc}",
                "form": dados,
            },
            status_code=502,
        )

    pdi = PDI(
        user_id=user.id,
        titulo=f"PDI - {objetivo[:60]}",
        cargo_atual=cargo_atual,
        nivel_experiencia=nivel_experiencia,
        area_interesse=area_interesse,
        objetivo=objetivo,
        tecnologias=tecnologias,
        horas_semanais=horas_semanais,
        conteudo_json=json.dumps(resultado, ensure_ascii=False),
    )
    session.add(pdi)
    session.commit()
    session.refresh(pdi)

    return RedirectResponse(f"/pdi/{pdi.id}", status_code=303)


@router.get("/pdi/{pdi_id}", response_class=HTMLResponse)
def ver_pdi(pdi_id: int, request: Request, session: Session = Depends(get_session)):
    user = _get_user(request, session)
    if not user:
        return RedirectResponse("/login", status_code=303)

    pdi = session.get(PDI, pdi_id)
    if not pdi or pdi.user_id != user.id:
        return RedirectResponse("/dashboard", status_code=303)

    conteudo = json.loads(pdi.conteudo_json)
    return templates.TemplateResponse(
        "pdi_detail.html",
        {"request": request, "user": user, "pdi": pdi, "c": conteudo},
    )
