from api.data import router as data_router

from fastapi import APIRouter

router = APIRouter(prefix="/api")

router.include_router(data_router)
