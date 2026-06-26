from datetime import datetime
from http import HTTPMethod
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

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
    cursor_created_at: datetime | None = None
    cursor_id: UUID | None = None

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized_method = value.upper()
        if normalized_method not in ALLOWED_METHODS:
            raise ValueError("Invalid HTTP method")

        return normalized_method

    @model_validator(mode="after")
    def validate_cursor(self) -> "LogEntryListQuery":
        has_cursor_created_at = self.cursor_created_at is not None
        has_cursor_id = self.cursor_id is not None

        if has_cursor_created_at != has_cursor_id:
            raise ValueError("Cursor parameters must be provided together")

        if has_cursor_created_at and self.offset != 0:
            raise ValueError("Offset must be 0 when cursor is used")

        return self


class LogEntryResponse(BaseModel):
    id: UUID
    created_at: datetime
    log: ParsedLogResponse


class LogEntryListResponse(BaseModel):
    items: list[LogEntryResponse]
    limit: int
    offset: int
    total: int
