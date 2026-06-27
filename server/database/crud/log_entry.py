from sqlalchemy import and_, func, or_, select
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

    if query.cursor_created_at is not None and query.cursor_id is not None:
        filters.append(
            or_(
                LogEntry.created_at > query.cursor_created_at,
                and_(
                    LogEntry.created_at == query.cursor_created_at,
                    LogEntry.id > query.cursor_id,
                ),
            )
        )

    total_stmt = select(func.count()).select_from(LogEntry)
    items_stmt = select(LogEntry)

    if filters:
        total_stmt = total_stmt.where(*filters)
        items_stmt = items_stmt.where(*filters)

    if query.cursor_created_at is not None and query.cursor_id is not None:
        items_stmt = items_stmt.order_by(LogEntry.created_at.asc(), LogEntry.id.asc())
    else:
        items_stmt = items_stmt.order_by(LogEntry.created_at.desc(), LogEntry.id.desc())

    items_stmt = items_stmt.offset(query.offset).limit(query.limit)

    total_result = await session.execute(total_stmt)
    items_result = await session.execute(items_stmt)

    return list(items_result.scalars().all()), total_result.scalar_one()


async def get_log_entry_stats(
    session: AsyncSession,
) -> tuple[dict[str, int], dict[str, int]]:
    methods_stmt = (
        select(LogEntry.method, func.count())
        .group_by(LogEntry.method)
        .order_by(LogEntry.method.asc())
    )
    status_codes_stmt = (
        select(LogEntry.status_code, func.count())
        .group_by(LogEntry.status_code)
        .order_by(LogEntry.status_code.asc())
    )

    methods_result = await session.execute(methods_stmt)
    status_codes_result = await session.execute(status_codes_stmt)

    methods = {
        method: count
        for method, count in methods_result.all()
    }
    status_codes = {
        str(status_code): count
        for status_code, count in status_codes_result.all()
    }

    return methods, status_codes
