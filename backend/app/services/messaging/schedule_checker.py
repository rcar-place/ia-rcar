"""
Verificador de horário comercial.
Usa o fuso horário America/Sao_Paulo conforme configurado.
"""
from datetime import datetime
import pytz

from app.core.config.settings import settings
from app.core.logger.logger import get_logger

logger = get_logger(__name__)

_tz = pytz.timezone(settings.TIMEZONE)


def get_current_time_local() -> datetime:
    """Retorna o horário atual no fuso configurado."""
    return datetime.now(_tz)


def is_business_hours(
    hour_start: int | None = None,
    hour_end: int | None = None,
) -> bool:
    """
    Verifica se o momento atual está dentro do horário comercial.

    Args:
        hour_start: hora de início (default: settings.BUSINESS_HOUR_START)
        hour_end: hora de fim (default: settings.BUSINESS_HOUR_END)

    Returns:
        True se estiver dentro do horário comercial.
    """
    start = hour_start if hour_start is not None else settings.BUSINESS_HOUR_START
    end = hour_end if hour_end is not None else settings.BUSINESS_HOUR_END

    now = get_current_time_local()
    current_hour = now.hour

    # Verifica se é dia útil (segunda=0 a sexta=4)
    is_weekday = now.weekday() < 5

    in_hours = start <= current_hour < end

    logger.debug(
        "Verificação de horário: %s | weekday=%s | hour=%d | start=%d | end=%d | inside=%s",
        now.strftime("%Y-%m-%d %H:%M"),
        is_weekday,
        current_hour,
        start,
        end,
        is_weekday and in_hours,
    )

    return is_weekday and in_hours


def should_ai_respond(
    hour_start: int | None = None,
    hour_end: int | None = None,
) -> bool:
    """
    Retorna True se a IA deve responder (fora do horário comercial).
    A IA SOMENTE responde quando a equipe humana NÃO está disponível.
    """
    return not is_business_hours(hour_start, hour_end)
