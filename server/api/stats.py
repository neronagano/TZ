import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.engine import get_session
from server.models.log_entry import LogEntryStatsResponse
from server.services.log_entry import get_log_entry_stats as get_log_entry_stats_service

router = APIRouter(prefix="/stats", tags=["Stats"])
logger = logging.getLogger(__name__)


@router.get("", response_model=LogEntryStatsResponse)
async def get_log_entry_stats(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    methods, status_codes = await get_log_entry_stats_service(session)

    logger.info(
        "log entry stats fetched",
        extra={
            "methods_count": len(methods),
            "status_codes_count": len(status_codes),
        },
    )

    return {
        "methods": methods,
        "status_codes": status_codes,
    }
