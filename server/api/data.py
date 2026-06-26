import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_session
from models.log import LogEntryCreateResponse
from services.log_entry import create_log_entry as create_log_entry_service
from services.log_parser import get_parsed_log

router = APIRouter(prefix="/data", tags=["Data"])
logger = logging.getLogger(__name__)


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
