"""
Middleware de tratamento global de erros.
Garante que stacktraces NUNCA vazem para o cliente em produção.
"""
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config.settings import settings
from app.core.logger.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Captura exceções não tratadas e retorna resposta genérica segura."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            # Log completo apenas no servidor
            logger.error(
                "Erro não tratado em %s %s: %s\n%s",
                request.method,
                request.url.path,
                type(exc).__name__,
                traceback.format_exc() if settings.DEBUG else "[oculto em produção]",
            )

            # Resposta genérica para o cliente (sem stacktrace)
            if settings.DEBUG:
                detail = f"{type(exc).__name__}: {str(exc)}"
            else:
                detail = "Erro interno. Por favor, tente novamente."

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": detail},
            )
