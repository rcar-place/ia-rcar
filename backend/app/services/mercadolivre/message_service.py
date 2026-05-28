"""
Serviço de integração com a API do Mercado Livre.
Responsável por enviar mensagens e gerenciar tokens.
"""
import httpx
from app.core.config.settings import settings
from app.core.logger.logger import get_logger

logger = get_logger(__name__)

BASE_URL = settings.ML_BASE_URL


async def send_message_to_ml(conversation_id: str, text: str) -> str:
    """
    Envia uma mensagem de resposta para o comprador via API do ML.

    Args:
        conversation_id: ID da conversa no ML
        text: texto da resposta

    Returns:
        ID da mensagem criada no ML

    Raises:
        RuntimeError: em caso de falha na API
    """
    url = f"{BASE_URL}/messages/packs/{conversation_id}/sellers/{settings.ML_SELLER_ID}"
    headers = {
        "Authorization": f"Bearer {settings.ML_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            ml_id = str(data.get("id", ""))
            logger.info("Mensagem enviada ao ML. ml_response_id=%s", ml_id)
            return ml_id
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.error("Erro HTTP ao enviar mensagem ao ML: status=%d", status_code)
            raise RuntimeError(f"ML API retornou status {status_code}") from exc
        except httpx.RequestError as exc:
            logger.error("Erro de conexão com ML API: %s", type(exc).__name__)
            raise RuntimeError("Falha de conexão com Mercado Livre") from exc


async def get_message_from_ml(message_id: str) -> dict:
    """Busca dados completos de uma mensagem no ML."""
    url = f"{BASE_URL}/messages/{message_id}"
    headers = {"Authorization": f"Bearer {settings.ML_ACCESS_TOKEN}"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Erro ao buscar mensagem %s no ML: %d", message_id, exc.response.status_code)
            raise RuntimeError(f"Falha ao buscar mensagem no ML: {exc.response.status_code}") from exc

async def get_item_from_ml(item_id: str) -> dict:
    """Busca dados básicos de um anúncio no ML (título, atributos, etc)."""
    url = f"{BASE_URL}/items/{item_id}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Erro ao buscar anúncio %s no ML: %d", item_id, exc.response.status_code)
            return {}
        except Exception as exc:
            logger.error("Erro de conexão ao buscar anúncio %s: %s", item_id, type(exc).__name__)
            return {}
