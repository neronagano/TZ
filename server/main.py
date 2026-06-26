from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from api import router
from database.engine import init_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
