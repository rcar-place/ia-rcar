"""
Middleware de logging de requisições.
Registra método, path, status e tempo de resposta.
Nunca loga headers de autorização.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger.logger import get_logger

logger = get_logger(__name__)

# Paths que não precisam ser logados (reduz ruído)
SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/ws/updates"}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        start = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000, 2)

        logger.info(
            "%s %s → %d [%sms] ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request.client.host if request.client else "-",
        )
        return response
