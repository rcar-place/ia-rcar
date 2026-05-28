"""
Serviço de integração com a API do Google Gemini.
Gera respostas seguras e rastreáveis para mensagens de compradores.
"""
import google.generativeai as genai

from app.core.config.settings import settings
from app.core.logger.logger import get_logger
from app.prompts.system_prompt import build_gemini_prompt, SYSTEM_PROMPT
from app.services.gemini.safety_filter import check_outgoing_response

logger = get_logger(__name__)

_is_configured = False


def get_gemini_model() -> genai.GenerativeModel:
    global _is_configured
    if not _is_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _is_configured = True
    
    return genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT
    )


async def generate_response(
    buyer_message: str, 
    item_context: str | None = None,
    max_tokens: int | None = None
) -> tuple[str, int, float]:
    """
    Gera uma resposta segura usando o modelo Gemini.
    """
    model = get_gemini_model()
    prompt = build_gemini_prompt(buyer_message, item_context)

    logger.info("Solicitando resposta ao Gemini para mensagem de %s chars", len(buyer_message))

    try:
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
            )
        )
    except Exception as exc:
        logger.error("Erro na API Gemini: %s", type(exc).__name__)
        raise RuntimeError("Serviço de IA temporariamente indisponível") from exc

    response_text = response.text if response.parts else ""
    tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
    finish_reason = getattr(response.candidates[0], "finish_reason", "unknown") if response.candidates else "no_candidates"
    logger.info("Finish reason: %s, max_tokens configured: %s", finish_reason, max_tokens or settings.GEMINI_MAX_TOKENS)

    # Calcula score aproximado de confiança (Gemini não expõe prob token por token da mesma forma que logprobs na mesma camada, mockamos 0.85 por enquanto)
    confidence = 0.85

    # Verifica segurança da resposta gerada
    filter_result = check_outgoing_response(response_text)
    if not filter_result.is_safe:
        logger.error(
            "Resposta da IA bloqueada pelo filtro: %s",
            filter_result.reason,
        )
        raise RuntimeError(f"Resposta bloqueada: {filter_result.reason}")

    logger.info(
        "Resposta gerada com sucesso: %s tokens, %s chars",
        tokens_used,
        len(response_text),
    )
    return response_text, tokens_used, confidence
