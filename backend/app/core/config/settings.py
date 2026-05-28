"""
Configurações centralizadas do sistema.
Usa pydantic-settings para carregar e validar variáveis de ambiente.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Aplicação ──────────────────────────────────────────────────────────
    APP_NAME: str = "ML AutoResponder"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ── Servidor ───────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── Banco de Dados ─────────────────────────────────────────────────────
    DATABASE_URL: str  # mysql+aiomysql://user:pass@host:3306/db
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # ── Segurança JWT ──────────────────────────────────────────────────────
    SECRET_KEY: str  # openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ───────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str | List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list) -> list:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    # ── Mercado Livre ──────────────────────────────────────────────────────
    ML_CLIENT_ID: str
    ML_CLIENT_SECRET: str
    ML_ACCESS_TOKEN: str
    ML_REFRESH_TOKEN: str
    ML_WEBHOOK_SECRET: str  # para validação HMAC
    ML_BASE_URL: str = "https://api.mercadolibre.com"
    ML_SELLER_ID: str

    # ── Google Gemini ────────────────────────────────────────────────────────
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_MAX_TOKENS: int = 300
    GEMINI_TEMPERATURE: float = 0.3

    # ── Horário Comercial (America/Sao_Paulo) ──────────────────────────────
    BUSINESS_HOUR_START: int = 8   # 08:00
    BUSINESS_HOUR_END: int = 18    # 18:00
    TIMEZONE: str = "America/Sao_Paulo"

    # ── Rate Limiting ──────────────────────────────────────────────────────
    RATE_LIMIT_WEBHOOK: str = "100/minute"
    RATE_LIMIT_API: str = "200/minute"

    # ── Redis (opcional — para rate limiting distribuído) ──────────────────
    REDIS_URL: str = "redis://localhost:6379/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
