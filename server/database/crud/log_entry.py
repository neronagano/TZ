from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.models.log_entry import LogEntry
from server.models.log_entry import LogEntryListQuery


async def create_log_entry(
    session: AsyncSession,
    parsed_log: dict[str, str | int],
) -> LogEntry:
    log_entry = LogEntry(**parsed_log)

    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)

    return log_entry


async def get_log_entries(
    session: AsyncSession,
    query: LogEntryListQuery,
) -> tuple[list[LogEntry], int]:
    filters = []

    if query.method is not None:
        filters.append(LogEntry.method == query.method)

    if query.status_code is not None:
        filters.append(LogEntry.status_code == query.status_code)

    total_stmt = select(func.count()).select_from(LogEntry)
    items_stmt = select(LogEntry)

    if filters:
        total_stmt = total_stmt.where(*filters)
        items_stmt = items_stmt.where(*filters)

    items_stmt = (
        items_stmt
        .order_by(LogEntry.created_at.desc())
        .offset(query.offset)
        .limit(query.limit)
    )

    total_result = await session.execute(total_stmt)
    items_result = await session.execute(items_stmt)

    return list(items_result.scalars().all()), total_result.scalar_one()
