"""Rotas de Logs do sistema."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.log import LogLevel, LogEvent
from app.repositories.log_repository import LogRepository

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/")
async def list_logs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    level: LogLevel | None = Query(default=None),
    event: LogEvent | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict:
    """Lista logs do sistema com paginação."""
    repo = LogRepository(db)
    items, total = await repo.list(page=page, per_page=per_page, level=level, event=event)

    return {
        "items": [
            {
                "id": log.id,
                "level": log.level,
                "event": log.event,
                "message": log.message,
                "message_id": log.message_id,
                "created_at": log.created_at.isoformat(),
            }
            for log in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }
