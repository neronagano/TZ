import logging
from json import loads
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_session
from models.log import LogEntryCreateResponse, LogEntryListQuery, LogEntryListResponse
from services.log_entry import create_log_entry as create_log_entry_service
from services.log_entry import get_log_entries as get_log_entries_service
from services.log_parser import get_parsed_log

router = APIRouter(prefix="/data", tags=["Data"])
logger = logging.getLogger(__name__)


def get_log_entries_query(
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    method: Annotated[str | None, Query()] = None,
    status_code: Annotated[int | None, Query(ge=100, le=599)] = None,
) -> LogEntryListQuery:
    try:
        return LogEntryListQuery(
            limit=limit,
            offset=offset,
            method=method,
            status_code=status_code,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=loads(exc.json()),
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LogEntryCreateResponse)
async def create_log_entry(
    parsed_log: Annotated[dict[str, str | int], Depends(get_parsed_log)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    logger.info("log entry request parsed", extra=parsed_log)
    log_entry = await create_log_entry_service(session, parsed_log)

    logger.info(
        "log entry saved",
        extra={"id": str(log_entry.id), "status_code": log_entry.status_code},
    )

    return {
        "id": log_entry.id,
        "created_at": log_entry.created_at,
        "log": parsed_log,
    }


@router.get("/", response_model=LogEntryListResponse)
async def get_log_entries(
    query: Annotated[LogEntryListQuery, Depends(get_log_entries_query)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    log_entries, total = await get_log_entries_service(session, query)

    logger.info(
        "log entries fetched",
        extra={
            "limit": query.limit,
            "offset": query.offset,
            "total": total,
            "method": query.method,
            "status_code": query.status_code,
        },
    )

    items = [
        {
            "id": log_entry.id,
            "created_at": log_entry.created_at,
            "log": {
                "ip": log_entry.ip,
                "method": log_entry.method,
                "uri": log_entry.uri,
                "status_code": log_entry.status_code,
            },
        }
        for log_entry in log_entries
    ]

    return {
        "items": items,
        "limit": query.limit,
        "offset": query.offset,
        "total": total,
    }
