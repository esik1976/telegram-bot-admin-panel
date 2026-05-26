from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import SESSION_COOKIE_NAME, create_session_token, require_admin, verify_admin_password
from app.config import Settings, get_settings
from app.db import get_db
from app.services.dashboard import get_dashboard_stats
from app.services.logs import list_errors, list_messages, list_users
from app.services.settings import (
    create_prompt_version,
    get_active_prompt,
    get_active_settings,
    update_active_settings,
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "Вход",
            "error": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    password: str = Form(...),
    settings: Settings = Depends(get_settings),
) -> Response:
    if not verify_admin_password(password, settings):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": "Вход",
                "error": "Неверный пароль администратора.",
            },
            status_code=401,
        )

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        create_session_token(settings),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


@router.post("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    stats = get_dashboard_stats(db)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Telegram Bot Admin Panel",
            "active_page": "dashboard",
            **stats,
        },
    )


@router.get("/prompts", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def prompts_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    prompt = get_active_prompt(db)
    return templates.TemplateResponse(
        "prompts.html",
        {
            "request": request,
            "title": "System Prompt",
            "active_page": "prompts",
            "prompt": prompt,
            "saved": False,
        },
    )


@router.post("/prompts", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def save_prompt(
    request: Request,
    content: str = Form(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    prompt = create_prompt_version(db, content)
    return templates.TemplateResponse(
        "prompts.html",
        {
            "request": request,
            "title": "System Prompt",
            "active_page": "prompts",
            "prompt": prompt,
            "saved": True,
        },
    )


@router.get("/settings", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def settings_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    settings = get_active_settings(db)
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Model Settings",
            "active_page": "settings",
            "settings": settings,
            "saved": False,
        },
    )


@router.post("/settings", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def save_settings(
    request: Request,
    provider: str = Form(...),
    model: str = Form(...),
    temperature: float = Form(...),
    max_tokens: int = Form(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    settings = update_active_settings(
        db,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Model Settings",
            "active_page": "settings",
            "settings": settings,
            "saved": True,
        },
    )


@router.get("/users", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def users_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "title": "Users",
            "active_page": "users",
            "users": list_users(db),
        },
    )


@router.get("/messages", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def messages_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "title": "Messages",
            "active_page": "messages",
            "messages": list_messages(db),
        },
    )


@router.get("/errors", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def errors_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    return templates.TemplateResponse(
        "errors.html",
        {
            "request": request,
            "title": "Errors",
            "active_page": "errors",
            "errors": list_errors(db),
        },
    )
