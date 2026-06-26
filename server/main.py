import logging

from fastapi import FastAPI
import uvicorn

from api import router
from core.logging import configure_logging

configure_logging()

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    logger.info("starting uvicorn server")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
