from datetime import datetime
from http import HTTPMethod
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

ALLOWED_METHODS = {
    HTTPMethod.GET.value,
    HTTPMethod.POST.value,
    HTTPMethod.PUT.value,
    HTTPMethod.PATCH.value,
    HTTPMethod.DELETE.value,
}


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


class LogEntryListQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    method: str | None = None
    status_code: int | None = Field(default=None, ge=100, le=599)

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized_method = value.upper()
        if normalized_method not in ALLOWED_METHODS:
            raise ValueError("Invalid HTTP method")

        return normalized_method


class LogEntryResponse(BaseModel):
    id: UUID
    created_at: datetime
    log: ParsedLogResponse


class LogEntryListResponse(BaseModel):
    items: list[LogEntryResponse]
    limit: int
    offset: int
    total: int
