"""
Orquestrador principal do sistema de mensagens.
Coordena: validação → armazenamento → IA → segurança → envio → WebSocket.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger.logger import get_logger
from app.models.message import MessageStatus
from app.models.log import LogLevel, LogEvent
from app.models.response import ResponseStatus
from app.models.setting import SettingKeys
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository
from app.repositories.log_repository import LogRepository
from app.repositories.setting_repository import SettingRepository
from app.services.messaging.schedule_checker import should_ai_respond
from app.services.gemini.ai_service import generate_response
from app.services.gemini.safety_filter import check_incoming_message, check_blacklist
from app.services.mercadolivre.message_service import send_message_to_ml, get_item_from_ml
from app.websocket.connection_manager import manager
from app.utils.sanitizer import sanitize_text

logger = get_logger(__name__)


async def process_incoming_message(
    session: AsyncSession,
    ml_message_id: str,
    ml_conversation_id: str,
    ml_buyer_id: str,
    ml_buyer_nickname: str | None,
    ml_item_id: str | None,
    raw_text: str,
) -> dict:
    """
    Orquestra o processamento completo de uma mensagem recebida do ML.

    Fluxo:
    1. Verifica duplicidade
    2. Sanitiza e salva mensagem
    3. Verifica horário comercial
    4. Verifica IA habilitada
    5. Filtra conteúdo inseguro
    6. Verifica blacklist
    7. Gera resposta com IA
    8. Filtra resposta
    9. Verifica aprovação manual
    10. Envia ao ML
    11. Notifica WebSocket
    """
    msg_repo = MessageRepository(session)
    resp_repo = ResponseRepository(session)
    log_repo = LogRepository(session)
    settings_repo = SettingRepository(session)

    # 1. Verifica duplicidade
    existing = await msg_repo.get_by_ml_id(ml_message_id)
    if existing:
        logger.info("Mensagem duplicada ignorada: %s", ml_message_id)
        return {"status": "duplicate", "message_id": existing.id}

    # 2. Sanitiza e salva mensagem
    text_sanitized = sanitize_text(raw_text)
    outside_hours = should_ai_respond(
        hour_start=await settings_repo.get_int(SettingKeys.BUSINESS_HOUR_START),
        hour_end=await settings_repo.get_int(SettingKeys.BUSINESS_HOUR_END),
    )

    message = await msg_repo.create({
        "ml_message_id": ml_message_id,
        "ml_conversation_id": ml_conversation_id,
        "ml_buyer_id": ml_buyer_id,
        "ml_buyer_nickname": ml_buyer_nickname,
        "ml_item_id": ml_item_id,
        "text": raw_text[:2000],
        "text_sanitized": text_sanitized,
        "status": MessageStatus.RECEIVED,
        "is_outside_business_hours": outside_hours,
    })

    await log_repo.create(
        level=LogLevel.INFO,
        event=LogEvent.MESSAGE_SAVED,
        message=f"Mensagem salva: {ml_message_id}",
        message_id=message.id,
    )

    # Notifica frontend em tempo real
    await manager.broadcast("message_received", {
        "id": message.id,
        "buyer": ml_buyer_nickname or ml_buyer_id,
        "status": message.status,
        "outside_hours": outside_hours,
    })

    # 3. Verifica horário comercial
    if not outside_hours:
        await msg_repo.update_status(message.id, MessageStatus.IGNORED)
        await log_repo.create(
            level=LogLevel.INFO,
            event=LogEvent.BUSINESS_HOURS,
            message="Mensagem ignorada — dentro do horário comercial",
            message_id=message.id,
        )
        logger.info("Mensagem ignorada (horário comercial): %s", ml_message_id)
        return {"status": "ignored_business_hours", "message_id": message.id}

    # 4. Verifica IA habilitada
    ai_enabled = await settings_repo.get_bool(SettingKeys.AI_ENABLED, default=True)
    if not ai_enabled:
        await msg_repo.update_status(message.id, MessageStatus.IGNORED)
        logger.info("IA desabilitada — mensagem ignorada: %s", ml_message_id)
        return {"status": "ai_disabled", "message_id": message.id}

    # 5. Filtra conteúdo inseguro da mensagem recebida
    filter_result = check_incoming_message(text_sanitized)

    if filter_result.is_injection_attempt:
        await msg_repo.update_status(message.id, MessageStatus.PROCESSING)
        # Responde normalmente sem revelar o filtro
        logger.warning("Prompt injection detectado para msg %d — respondendo normalmente", message.id)
        injected_response = "Olá! Obrigado pelo seu contato. Nossa equipe retornará em breve no horário comercial (08h-18h). 😊"
        await _send_and_save_response(
            session, message.id, ml_conversation_id, injected_response,
            resp_repo, log_repo, msg_repo, was_filtered=True, filter_reason="injection"
        )
        return {"status": "processed", "message_id": message.id}

    if filter_result.is_threat:
        await msg_repo.update_status(message.id, MessageStatus.PENDING_APPROVAL)
        message.requires_manual_review = True
        await log_repo.create(
            level=LogLevel.WARNING,
            event=LogEvent.AI_BLOCKED,
            message="Mensagem com conteúdo de ameaça — aguardando revisão manual",
            message_id=message.id,
        )
        await manager.broadcast("manual_review_required", {"message_id": message.id})
        return {"status": "pending_manual_review", "message_id": message.id}

    # 6. Verifica blacklist
    blacklist_raw = await settings_repo.get(SettingKeys.BLACKLIST_WORDS) or ""
    blacklist = [w.strip() for w in blacklist_raw.split(",") if w.strip()]
    if check_blacklist(text_sanitized, blacklist):
        await msg_repo.update_status(message.id, MessageStatus.PENDING_APPROVAL)
        return {"status": "blacklist_match", "message_id": message.id}

    # 7 & 8. Gera resposta com IA
    await msg_repo.update_status(message.id, MessageStatus.PROCESSING)
    await log_repo.create(
        level=LogLevel.INFO,
        event=LogEvent.AI_REQUESTED,
        message="Solicitando resposta à IA",
        message_id=message.id,
    )

    item_context = None
    if ml_item_id:
        item_data = await get_item_from_ml(ml_item_id)
        if item_data and "title" in item_data:
            title = item_data.get("title", "")
            price = item_data.get("price", "")
            attributes = ", ".join([f"{attr.get('name')}: {attr.get('value_name')}" for attr in item_data.get("attributes", [])[:5]])
            item_context = f"Título: {title} | Preço: {price} | Detalhes: {attributes}"

    try:
        response_text, tokens, confidence = await generate_response(text_sanitized, item_context)
    except RuntimeError as exc:
        await msg_repo.update_status(message.id, MessageStatus.ERROR)
        await log_repo.create(
            level=LogLevel.ERROR,
            event=LogEvent.AI_BLOCKED,
            message=f"Erro na IA: {exc}",
            message_id=message.id,
        )
        return {"status": "ai_error", "message_id": message.id}

    # 9. Verifica aprovação manual
    manual_required = await settings_repo.get_bool(SettingKeys.MANUAL_APPROVAL_REQUIRED, default=False)
    confidence_threshold = await settings_repo.get_float(SettingKeys.AI_CONFIDENCE_THRESHOLD, default=0.7)

    if manual_required or confidence < confidence_threshold:
        response = await resp_repo.create({
            "message_id": message.id,
            "text": response_text,
            "model_used": "gemini-2.5-flash",
            "tokens_used": tokens,
            "confidence_score": confidence,
            "status": ResponseStatus.GENERATED,
        })
        await msg_repo.update_status(message.id, MessageStatus.PENDING_APPROVAL)
        await manager.broadcast("pending_approval", {
            "message_id": message.id,
            "response_id": response.id,
            "confidence": confidence,
        })
        return {"status": "pending_approval", "message_id": message.id}

    # 10. Envia ao ML
    await _send_and_save_response(
        session, message.id, ml_conversation_id, response_text,
        resp_repo, log_repo, msg_repo,
        tokens=tokens, confidence=confidence
    )
    return {"status": "responded", "message_id": message.id}


async def _send_and_save_response(
    session: AsyncSession,
    message_id: int,
    ml_conversation_id: str,
    response_text: str,
    resp_repo: ResponseRepository,
    log_repo: LogRepository,
    msg_repo: MessageRepository,
    tokens: int = 0,
    confidence: float = 1.0,
    was_filtered: bool = False,
    filter_reason: str | None = None,
) -> None:
    """Envia resposta ao ML e salva no banco."""
    try:
        ml_response_id = await send_message_to_ml(ml_conversation_id, response_text)
        status = ResponseStatus.SENT
        msg_status = MessageStatus.RESPONDED
        log_event = LogEvent.RESPONSE_SENT
        log_level = LogLevel.INFO
        log_msg = f"Resposta enviada ao ML: {ml_response_id}"
    except Exception as exc:
        ml_response_id = None
        status = ResponseStatus.FAILED
        msg_status = MessageStatus.ERROR
        log_event = LogEvent.RESPONSE_FAILED
        log_level = LogLevel.ERROR
        log_msg = f"Falha ao enviar resposta ao ML: {exc}"

    response = await resp_repo.create({
        "message_id": message_id,
        "text": response_text,
        "model_used": "gemini-2.5-flash",
        "tokens_used": tokens,
        "confidence_score": confidence,
        "was_filtered": was_filtered,
        "filter_reason": filter_reason,
        "status": status,
        "ml_response_id": ml_response_id,
    })

    await msg_repo.update_status(message_id, msg_status)
    await log_repo.create(
        level=log_level,
        event=log_event,
        message=log_msg,
        message_id=message_id,
    )

    # Notifica frontend
    await manager.broadcast("response_sent", {
        "message_id": message_id,
        "response_id": response.id,
        "status": str(status),
    })
