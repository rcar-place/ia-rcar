"""
Repositório de Mensagens.
Abstrai o acesso ao banco de dados para a entidade Message.
"""
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message, MessageStatus


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict) -> Message:
        message = Message(**data)
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        result = await self._session.execute(
            select(Message)
            .options(selectinload(Message.response))
            .where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ml_id(self, ml_message_id: str) -> Message | None:
        result = await self._session.execute(
            select(Message).where(Message.ml_message_id == ml_message_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        per_page: int = 20,
        status: MessageStatus | None = None,
    ) -> tuple[list[Message], int]:
        query = select(Message).options(selectinload(Message.response))

        if status:
            query = query.where(Message.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._session.execute(count_query)).scalar_one()

        query = query.order_by(desc(Message.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)
        results = (await self._session.execute(query)).scalars().all()

        return list(results), total

    async def update_status(self, message_id: int, status: MessageStatus) -> None:
        message = await self.get_by_id(message_id)
        if message:
            message.status = status
            await self._session.flush()

    async def count_by_status(self) -> dict[str, int]:
        result = await self._session.execute(
            select(Message.status, func.count(Message.id))
            .group_by(Message.status)
        )
        return {str(row[0]): row[1] for row in result.all()}
