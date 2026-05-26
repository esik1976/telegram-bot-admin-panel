from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.web.routes import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="Telegram Bot Admin Panel")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(api_router)
    app.include_router(web_router)
    return app


app = create_app()
