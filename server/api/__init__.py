from fastapi import APIRouter
from server.api.data import router as data_router
from server.api.stats import router as stats_router

router = APIRouter(prefix="/api")

router.include_router(data_router)
router.include_router(stats_router)
