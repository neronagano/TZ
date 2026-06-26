import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.log_entry import create_log_entry as create_log_entry_crud
from database.crud.log_entry import get_log_entries as get_log_entries_crud
from database.models.log_entry import LogEntry
from models.log_entry import LogEntryListQuery

logger = logging.getLogger(__name__)


async def create_log_entry(
    session: AsyncSession,
    parsed_log: dict[str, str | int],
) -> LogEntry:
    try:
        return await create_log_entry_crud(session, parsed_log)
    except SQLAlchemyError:
        await session.rollback()
        logger.exception("failed to save log entry")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def get_log_entries(
    session: AsyncSession,
    query: LogEntryListQuery,
) -> tuple[list[LogEntry], int]:
    try:
        return await get_log_entries_crud(session, query)
    except SQLAlchemyError:
        logger.exception("failed to fetch log entries")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
