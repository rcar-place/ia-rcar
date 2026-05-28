"""
Repositório de Respostas geradas pela IA.
"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.response import Response, ResponseStatus


class ResponseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict) -> Response:
        response = Response(**data)
        self._session.add(response)
        await self._session.flush()
        await self._session.refresh(response)
        return response

    async def get_by_message_id(self, message_id: int) -> Response | None:
        result = await self._session.execute(
            select(Response).where(Response.message_id == message_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        response_id: int,
        status: ResponseStatus,
        ml_response_id: str | None = None,
    ) -> None:
        result = await self._session.execute(
            select(Response).where(Response.id == response_id)
        )
        response = result.scalar_one_or_none()
        if response:
            response.status = status
            if ml_response_id:
                response.ml_response_id = ml_response_id
            await self._session.flush()

    async def list_recent(self, limit: int = 50) -> list[Response]:
        result = await self._session.execute(
            select(Response).order_by(desc(Response.created_at)).limit(limit)
        )
        return list(result.scalars().all())
