"""
Repositório de Logs do sistema.
"""
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import Log, LogLevel, LogEvent


class LogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        level: LogLevel,
        event: LogEvent,
        message: str,
        details: dict | None = None,
        message_id: int | None = None,
        user_id: int | None = None,
        ip_address: str | None = None,
    ) -> Log:
        log = Log(
            level=level,
            event=event,
            message=message,
            details=details,
            message_id=message_id,
            user_id=user_id,
            ip_address=ip_address,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def list(
        self,
        page: int = 1,
        per_page: int = 50,
        level: LogLevel | None = None,
        event: LogEvent | None = None,
    ) -> tuple[list[Log], int]:
        query = select(Log)
        if level:
            query = query.where(Log.level == level)
        if event:
            query = query.where(Log.event == event)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._session.execute(count_query)).scalar_one()

        query = query.order_by(desc(Log.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)
        results = (await self._session.execute(query)).scalars().all()

        return list(results), total
