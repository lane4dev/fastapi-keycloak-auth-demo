from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.router import router as api_router
from src.config import settings


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name, debug=settings.debug, version=settings.app_version
    )

    application.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = get_application()
