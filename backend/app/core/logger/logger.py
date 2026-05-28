"""
Logger estruturado com suporte a JSON e sanitização de dados sensíveis.
Em produção usa formato JSON; em desenvolvimento usa formato legível.
"""
import logging
import re
import sys
from typing import Any

from app.core.config.settings import settings

# Padrões de dados sensíveis a serem mascarados nos logs
SENSITIVE_PATTERNS = [
    (re.compile(r'(access_token["\s:=]+)[^\s,}&"]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(refresh_token["\s:=]+)[^\s,}&"]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(password["\s:=]+)[^\s,}&"]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(secret["\s:=]+)[^\s,}&"]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(authorization:\s*bearer\s+)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(api[_-]?key["\s:=]+)[^\s,}&"]+', re.IGNORECASE), r'\1[REDACTED]'),
]


def sanitize_log_message(message: str) -> str:
    """Remove dados sensíveis de mensagens de log."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


class SanitizingFormatter(logging.Formatter):
    """Formatter que sanitiza automaticamente dados sensíveis."""

    def format(self, record: logging.LogRecord) -> str:
        record.msg = sanitize_log_message(str(record.msg))
        if record.args:
            # Sanitiza argumentos do log
            if isinstance(record.args, dict):
                record.args = {
                    k: sanitize_log_message(str(v))
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_log_message(str(a)) for a in record.args
                )
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado e sanitizado."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        # Formato JSON para produção (facilita indexação por ferramentas de log)
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","msg":%(message)s}'
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    formatter = SanitizingFormatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
