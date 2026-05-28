"""
Gerenciador de conexões WebSocket.
Mantém conexões ativas e faz broadcast de atualizações em tempo real.
"""
import json
from typing import Any
from fastapi import WebSocket
from app.core.logger.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Gerencia múltiplas conexões WebSocket ativas."""

    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.append(websocket)
        logger.info("WebSocket conectado. Total: %d", len(self._active))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._active:
            self._active.remove(websocket)
        logger.info("WebSocket desconectado. Total: %d", len(self._active))

    async def broadcast(self, event_type: str, data: Any) -> None:
        """Envia uma mensagem para todas as conexões ativas."""
        if not self._active:
            return

        payload = json.dumps({"type": event_type, "data": data})
        dead = []

        for connection in self._active:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)

        for conn in dead:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, event_type: str, data: Any) -> None:
        """Envia mensagem apenas para uma conexão específica."""
        payload = json.dumps({"type": event_type, "data": data})
        await websocket.send_text(payload)

    @property
    def connection_count(self) -> int:
        return len(self._active)


# Instância singleton
manager = ConnectionManager()
