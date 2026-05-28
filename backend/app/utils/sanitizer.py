"""
Sanitização de entradas do usuário e mensagens externas.
Previne XSS e SQL Injection via camada de aplicação (ORM já previne a nível de DB).
"""
import re
import html

# Máximo de caracteres aceitos numa mensagem de webhook
MAX_MESSAGE_LENGTH = 2000
MAX_FIELD_LENGTH = 500


def sanitize_text(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """
    Sanitiza texto de entrada:
    - Remove tags HTML
    - Codifica caracteres especiais
    - Limita tamanho
    - Remove caracteres de controle
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove tags HTML
    text = re.sub(r"<[^>]+>", "", text)

    # Escapa entidades HTML
    text = html.escape(text, quote=True)

    # Remove caracteres de controle (exceto espaços, tabs e newlines)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Limita tamanho
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def sanitize_field(text: str) -> str:
    """Sanitiza campos menores (nomes, IDs, etc.)."""
    return sanitize_text(text, max_length=MAX_FIELD_LENGTH)


def sanitize_log_detail(data: dict) -> dict:
    """
    Remove dados sensíveis de dicionários antes de salvar em log.
    """
    SENSITIVE_KEYS = {
        "password", "token", "secret", "access_token", "refresh_token",
        "api_key", "authorization", "credential",
    }
    return {
        k: "[REDACTED]" if k.lower() in SENSITIVE_KEYS else v
        for k, v in data.items()
    }
