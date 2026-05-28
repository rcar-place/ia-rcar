"""
Rota WebSocket para atualizações em tempo real.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import manager
from app.core.logger.logger import get_logger

router = APIRouter(tags=["WebSocket"])
logger = get_logger(__name__)


@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Canal WebSocket para o frontend receber atualizações em tempo real:
    - Novas mensagens recebidas
    - Respostas enviadas
    - Eventos de aprovação manual
    """
    await manager.connect(websocket)
    try:
        # Mantém a conexão aberta
        while True:
            # Aguarda mensagens do cliente (ping/pong ou comandos)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.debug("WebSocket desconectado normalmente")
    except Exception as exc:
        manager.disconnect(websocket)
        logger.error("Erro no WebSocket: %s", type(exc).__name__)
