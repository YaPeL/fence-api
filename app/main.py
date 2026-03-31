from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import register_exception_handlers
from app.api import router as health_router
from app.core.logging import configure_logging
from app.core.observability import request_logging_middleware
from app.core.settings import settings

configure_logging()
log = logging.getLogger("app")

app = FastAPI(title=settings.service_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "content-type", "Accept"],
)
app.middleware("http")(request_logging_middleware)
app.include_router(health_router, tags=["health"])

register_exception_handlers(app)

