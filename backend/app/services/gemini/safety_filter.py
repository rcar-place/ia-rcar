"""
Filtro de segurança para respostas da IA.
Detecta prompt injection, conteúdo sensível e mensagens de risco.
"""
import re
from dataclasses import dataclass
from app.core.logger.logger import get_logger

logger = get_logger(__name__)

# Padrões de prompt injection
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(suas?\s+)?instru[çc][oõ]es",
    r"mostre?\s+(seus?\s+)?prompt",
    r"finja\s+ser\s+(administrador|admin|deus|root)",
    r"revele?\s+(seus?\s+)?(tokens?|secrets?|senhas?|credenciais?)",
    r"ignore\s+(as\s+)?regras",
    r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
    r"forget\s+(all\s+)?previous\s+instructions?",
    r"ignore\s+all\s+previous",
    r"act\s+as\s+(if\s+you\s+are\s+)?",
    r"pretend\s+(you\s+are\s+|to\s+be\s+)",
    r"jailbreak",
    r"bypass\s+(your\s+)?filter",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[SYSTEM\]",
    r"\[INST\]",
]

# Palavras que indicam ameaças (requerem revisão manual)
THREAT_PATTERNS = [
    r"\b(processo|ação\s+judicial|advogado|procon|tribunal)\b",
    r"\b(ameaça|ameaço|processo\s+judicial)\b",
    r"\b(matar|morre|violência)\b",
]

# Dados que não devem aparecer em respostas
SENSITIVE_DATA_PATTERNS = [
    r"\b[A-Za-z0-9]{20,}\b",  # Possíveis tokens longos
    r"sk-[A-Za-z0-9]{20,}",   # OpenAI keys
    r"AIza[0-9A-Za-z-_]{35}", # Gemini API Keys
    r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
]

compiled_injection = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]
compiled_threats = [re.compile(p, re.IGNORECASE) for p in THREAT_PATTERNS]
compiled_sensitive = [re.compile(p) for p in SENSITIVE_DATA_PATTERNS]


@dataclass
class FilterResult:
    is_safe: bool
    reason: str | None
    is_threat: bool
    is_injection_attempt: bool


def check_incoming_message(text: str) -> FilterResult:
    """
    Verifica a mensagem recebida do comprador.
    Detecta tentativas de prompt injection e ameaças.
    """
    for pattern in compiled_injection:
        if pattern.search(text):
            logger.warning("Tentativa de prompt injection detectada: %.50s...", text)
            return FilterResult(
                is_safe=False,
                reason="prompt_injection",
                is_threat=False,
                is_injection_attempt=True,
            )

    for pattern in compiled_threats:
        if pattern.search(text):
            logger.warning("Mensagem com conteúdo de ameaça detectada")
            return FilterResult(
                is_safe=False,
                reason="threat_content",
                is_threat=True,
                is_injection_attempt=False,
            )

    return FilterResult(is_safe=True, reason=None, is_threat=False, is_injection_attempt=False)


def check_outgoing_response(text: str) -> FilterResult:
    """
    Verifica a resposta gerada pela IA antes de enviar.
    Garante que não há dados sensíveis ou conteúdo inadequado.
    """
    for pattern in compiled_sensitive:
        if pattern.search(text):
            logger.error("Dado sensível detectado na resposta da IA — bloqueado")
            return FilterResult(
                is_safe=False,
                reason="sensitive_data_leak",
                is_threat=False,
                is_injection_attempt=False,
            )

    return FilterResult(is_safe=True, reason=None, is_threat=False, is_injection_attempt=False)


def check_blacklist(text: str, blacklist_words: list[str]) -> bool:
    """Verifica se a mensagem contém palavras da blacklist configurada pelo usuário."""
    text_lower = text.lower()
    for word in blacklist_words:
        if word.strip().lower() and word.strip().lower() in text_lower:
            logger.info("Palavra da blacklist detectada: [REDACTED]")
            return True
    return False
