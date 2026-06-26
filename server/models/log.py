from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LogCreateRequest(BaseModel):
    log: str


class ParsedLogResponse(BaseModel):
    ip: str
    method: str
    uri: str
    status_code: int


class LogEntryCreateResponse(BaseModel):
    id: UUID
    created_at: datetime
    log: ParsedLogResponse
