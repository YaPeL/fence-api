from fastapi import APIRouter

from app.api.routes.educa import router as educa_router
from app.api.routes.health import health
from app.api.routes.health import router as health_router
from app.api.routes.nomina import router as nomina_router
from app.api.routes.payearly import router as payearly_router

router = APIRouter()
router.include_router(health_router)
router.include_router(educa_router)
router.include_router(payearly_router)
router.include_router(nomina_router)

__all__ = ["health", "router"]
