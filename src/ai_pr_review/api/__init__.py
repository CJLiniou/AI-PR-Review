from fastapi import APIRouter

from .health import router as health_router
from .review import router as review_router

router = APIRouter(prefix="/api")
router.include_router(health_router)
router.include_router(review_router)
