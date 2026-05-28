"""
Rota de Webhook do Mercado Livre.
Recebe notificações, valida assinatura HMAC e processa mensagens.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.core.security.hmac_validator import validate_webhook_signature
from app.core.logger.logger import get_logger
from app.schemas.webhook import MLWebhookPayload
from app.services.messaging.orchestrator import process_incoming_message
from app.services.mercadolivre.message_service import get_message_from_ml

router = APIRouter(prefix="/webhook", tags=["Webhook"])
logger = get_logger(__name__)


@router.post("/mercadolivre", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Recebe notificações do Mercado Livre.

    Segurança:
    - Valida assinatura HMAC-SHA256
    - Valida schema do payload
    - Processa em background para responder rápido ao ML
    """
    # Lê body raw para validação HMAC
    raw_body = await request.body()
    signature = request.headers.get("x-signature")

    # Valida assinatura
    if not validate_webhook_signature(raw_body, signature):
        logger.warning(
            "Webhook com assinatura inválida recebido de: %s",
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura inválida",
        )

    # Valida payload
    try:
        import json
        payload_dict = json.loads(raw_body)
        payload = MLWebhookPayload(**payload_dict)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payload inválido",
        )

    # Processa apenas tópico de mensagens
    if payload.topic != "messages":
        logger.debug("Webhook ignorado (tópico: %s)", payload.topic)
        return {"status": "ignored"}

    # Extrai ID da mensagem do resource path (/messages/{id})
    resource_parts = payload.resource.strip("/").split("/")
    if len(resource_parts) < 2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resource inválido")

    message_id = resource_parts[-1]

    # Processa em background (ML espera resposta rápida)
    background_tasks.add_task(
        _process_message_background,
        db=db,
        ml_message_id=message_id,
    )

    logger.info("Webhook recebido e aceito: msg_id=%s", message_id)
    return {"status": "accepted"}


async def _process_message_background(db: AsyncSession, ml_message_id: str) -> None:
    """Busca detalhes da mensagem no ML e orquestra o processamento."""
    try:
        msg_data = await get_message_from_ml(ml_message_id)

        await process_incoming_message(
            session=db,
            ml_message_id=ml_message_id,
            ml_conversation_id=str(msg_data.get("pack_id") or msg_data.get("conversation_id", "")),
            ml_buyer_id=str(msg_data.get("from", {}).get("user_id", "")),
            ml_buyer_nickname=msg_data.get("from", {}).get("name"),
            ml_item_id=msg_data.get("order_id"),
            raw_text=msg_data.get("text", {}).get("plain", "") or "",
        )
    except Exception as exc:
        logger.error("Erro no processamento background da msg %s: %s", ml_message_id, type(exc).__name__)
