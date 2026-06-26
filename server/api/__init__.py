from fastapi import APIRouter
from server.api.data import router as data_router

router = APIRouter(prefix="/api")

router.include_router(data_router)
