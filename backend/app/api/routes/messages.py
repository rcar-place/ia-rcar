"""
Rotas de Mensagens.
Lista, filtra e aprova mensagens manualmente.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.message import MessageStatus
from app.models.setting import SettingKeys
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository
from app.repositories.log_repository import LogRepository
from app.repositories.setting_repository import SettingRepository
from app.schemas.message import MessageListResponse, MessageOut, ApproveRequest, DashboardStats
from app.services.mercadolivre.message_service import send_message_to_ml
from app.models.response import ResponseStatus
from app.models.log import LogLevel, LogEvent
from app.services.messaging.schedule_checker import is_business_hours
from app.websocket.connection_manager import manager

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/", response_model=MessageListResponse)
async def list_messages(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: MessageStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> MessageListResponse:
    """Lista mensagens com paginação e filtros."""
    repo = MessageRepository(db)
    items, total = await repo.list(page=page, per_page=per_page, status=status)
    return MessageListResponse(
        items=[MessageOut.model_validate(m) for m in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> DashboardStats:
    """Retorna estatísticas para o dashboard."""
    msg_repo = MessageRepository(db)
    settings_repo = SettingRepository(db)

    counts = await msg_repo.count_by_status()
    ai_enabled = await settings_repo.get_bool(SettingKeys.AI_ENABLED, default=True)
    business = is_business_hours(
        hour_start=await settings_repo.get_int(SettingKeys.BUSINESS_HOUR_START),
        hour_end=await settings_repo.get_int(SettingKeys.BUSINESS_HOUR_END),
    )

    return DashboardStats(
        total_messages=sum(counts.values()),
        responded=counts.get(MessageStatus.RESPONDED, 0),
        pending=counts.get(MessageStatus.PENDING_APPROVAL, 0) + counts.get(MessageStatus.PROCESSING, 0),
        ignored=counts.get(MessageStatus.IGNORED, 0),
        errors=counts.get(MessageStatus.ERROR, 0),
        ai_enabled=ai_enabled,
        is_business_hours=business,
        ws_connections=manager.connection_count,
    )


@router.get("/{message_id}", response_model=MessageOut)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> MessageOut:
    """Retorna detalhes de uma mensagem específica."""
    repo = MessageRepository(db)
    message = await repo.get_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    return MessageOut.model_validate(message)


@router.post("/{message_id}/approve", status_code=status.HTTP_200_OK)
async def approve_message(
    message_id: int,
    body: ApproveRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict:
    """
    Aprova ou rejeita o envio de uma resposta pendente de aprovação manual.
    """
    msg_repo = MessageRepository(db)
    resp_repo = ResponseRepository(db)
    log_repo = LogRepository(db)

    message = await msg_repo.get_by_id(message_id)
    if not message or message.status != MessageStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada ou não pendente")

    response = await resp_repo.get_by_message_id(message_id)
    if not response:
        raise HTTPException(status_code=404, detail="Resposta não encontrada")

    if body.approved:
        background_tasks.add_task(
            _send_approved_response,
            db=db,
            message=message,
            response=response,
            msg_repo=msg_repo,
            resp_repo=resp_repo,
            log_repo=log_repo,
        )
        return {"status": "sending"}
    else:
        await msg_repo.update_status(message_id, MessageStatus.REJECTED)
        await resp_repo.update_status(response.id, ResponseStatus.BLOCKED, None)
        await log_repo.create(
            level=LogLevel.INFO,
            event=LogEvent.MANUAL_APPROVAL,
            message=f"Resposta rejeitada manualmente. Motivo: {body.reason or 'N/A'}",
            message_id=message_id,
        )
        return {"status": "rejected"}


async def _send_approved_response(db, message, response, msg_repo, resp_repo, log_repo):
    """Envia resposta aprovada manualmente ao ML."""
    try:
        ml_id = await send_message_to_ml(message.ml_conversation_id, response.text)
        await resp_repo.update_status(response.id, ResponseStatus.SENT, ml_id)
        await msg_repo.update_status(message.id, MessageStatus.RESPONDED)
        await log_repo.create(
            level=LogLevel.INFO,
            event=LogEvent.RESPONSE_SENT,
            message=f"Resposta aprovada manualmente e enviada: {ml_id}",
            message_id=message.id,
        )
        await manager.broadcast("response_sent", {"message_id": message.id, "status": "sent"})
    except Exception as exc:
        await msg_repo.update_status(message.id, MessageStatus.ERROR)
        await log_repo.create(
            level=LogLevel.ERROR,
            event=LogEvent.RESPONSE_FAILED,
            message=f"Falha ao enviar resposta aprovada: {exc}",
            message_id=message.id,
        )

class TestAIRequest(BaseModel):
    message: str
    item_context: str | None = None


@router.post("/test-ai")
async def test_ai_agent(
    body: TestAIRequest,
    _user=Depends(get_current_user)
):
    """Rota para testar o agente de IA com contexto manual (Sandbox)"""
    from app.services.gemini.safety_filter import check_incoming_message
    from app.services.gemini.ai_service import generate_response

    filter_res = check_incoming_message(body.message)
    if not filter_res.is_safe:
        return {"response": f"[BLOQUEADO PELO FILTRO] Motivo: {filter_res.reason}"}

    try:
        response_text, tokens, conf = await generate_response(body.message, body.item_context)
        return {"response": response_text}
    except Exception as exc:
        return {"response": f"[ERRO DA IA] {exc}"}

