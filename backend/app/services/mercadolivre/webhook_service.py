"""
Serviço de webhook do Mercado Livre.
Processa e valida notificações recebidas.
"""
from app.core.logger.logger import get_logger

logger = get_logger(__name__)


def parse_resource_id(resource: str) -> str | None:
    """
    Extrai o ID do resource path do webhook.
    Exemplo: '/messages/123456789' → '123456789'
    """
    parts = resource.strip("/").split("/")
    if len(parts) >= 2:
        return parts[-1]
    return None
