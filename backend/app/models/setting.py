"""Model de Configuração do sistema (chave-valor)."""
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database.base import Base


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Setting key={self.key}>"


# Chaves de configuração padrão
class SettingKeys:
    AI_ENABLED = "ai_enabled"
    BUSINESS_HOUR_START = "business_hour_start"
    BUSINESS_HOUR_END = "business_hour_end"
    MANUAL_APPROVAL_REQUIRED = "manual_approval_required"
    AI_CONFIDENCE_THRESHOLD = "ai_confidence_threshold"
    BLACKLIST_WORDS = "blacklist_words"
    RESPONSE_LANGUAGE = "response_language"
    MAX_RESPONSE_LENGTH = "max_response_length"

DEFAULT_SETTINGS = {
    SettingKeys.AI_ENABLED: ("true", "Habilitar resposta automática da IA"),
    SettingKeys.BUSINESS_HOUR_START: ("8", "Início do horário comercial (hora)"),
    SettingKeys.BUSINESS_HOUR_END: ("18", "Fim do horário comercial (hora)"),
    SettingKeys.MANUAL_APPROVAL_REQUIRED: ("false", "Exigir aprovação manual antes de enviar"),
    SettingKeys.AI_CONFIDENCE_THRESHOLD: ("0.7", "Confiança mínima para envio automático (0-1)"),
    SettingKeys.BLACKLIST_WORDS: ("", "Palavras que bloqueiam resposta automática (separadas por vírgula)"),
    SettingKeys.RESPONSE_LANGUAGE: ("pt-BR", "Idioma das respostas"),
    SettingKeys.MAX_RESPONSE_LENGTH: ("500", "Tamanho máximo da resposta em caracteres"),
}
