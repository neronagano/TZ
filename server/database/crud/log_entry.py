from sqlalchemy.ext.asyncio import AsyncSession

from database.models.log_entry import LogEntry


async def create_log_entry(
    session: AsyncSession,
    parsed_log: dict[str, str | int],
) -> LogEntry:
    log_entry = LogEntry(**parsed_log)

    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)

    return log_entry
