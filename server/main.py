import logging

from fastapi import FastAPI
import uvicorn

from core.logging import configure_logging
from core.settings import settings
from server.api import router

configure_logging(include_uvicorn=True)

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    logger.info("starting uvicorn server")
    uvicorn.run(
        "server.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
