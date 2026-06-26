from pydantic import BaseModel


class LogCreateRequest(BaseModel):
    log: str
