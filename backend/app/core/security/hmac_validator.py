"""
Validação de webhooks do Mercado Livre via HMAC-SHA256.
Garante que as requisições vêm genuinamente do ML.
"""
import hashlib
import hmac
from app.core.config.settings import settings
from app.core.logger.logger import get_logger

logger = get_logger(__name__)


def validate_webhook_signature(
    payload: bytes,
    signature_header: str | None,
) -> bool:
    """
    Valida a assinatura HMAC-SHA256 do webhook do Mercado Livre.

    O ML envia o header 'x-signature' com o valor:
        ts=<timestamp>,v1=<hmac_hex>

    Args:
        payload: corpo raw da requisição (bytes)
        signature_header: valor do header x-signature

    Returns:
        True se a assinatura for válida, False caso contrário.
    """
    if not signature_header:
        logger.warning("Webhook recebido sem header x-signature")
        return False

    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp = parts.get("ts", "")
        received_sig = parts.get("v1", "")

        if not timestamp or not received_sig:
            logger.warning("Header x-signature malformado: %s", signature_header[:50])
            return False

        # Mensagem = timestamp + payload (sem newline)
        message = f"{timestamp}.".encode() + payload
        expected_sig = hmac.new(
            settings.ML_WEBHOOK_SECRET.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()

        valid = hmac.compare_digest(expected_sig, received_sig)
        if not valid:
            logger.warning("Assinatura HMAC inválida no webhook")
        return valid

    except Exception as exc:
        logger.error("Erro ao validar assinatura do webhook: %s", type(exc).__name__)
        return False
