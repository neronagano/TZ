import logging

from fastapi import FastAPI
import uvicorn

from api import router
from core.logging import configure_logging
from core.settings import settings

configure_logging()

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    logger.info("starting uvicorn server")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
