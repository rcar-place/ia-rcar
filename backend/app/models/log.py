"""Model de Log do sistema."""
import enum
from sqlalchemy import Enum, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database.base import Base


class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEvent(str, enum.Enum):
    WEBHOOK_RECEIVED = "webhook_received"
    WEBHOOK_INVALID = "webhook_invalid"
    MESSAGE_SAVED = "message_saved"
    AI_REQUESTED = "ai_requested"
    AI_RESPONDED = "ai_responded"
    AI_BLOCKED = "ai_blocked"
    RESPONSE_SENT = "response_sent"
    RESPONSE_FAILED = "response_failed"
    BUSINESS_HOURS = "business_hours"
    MANUAL_APPROVAL = "manual_approval"
    AUTH_LOGIN = "auth_login"
    AUTH_FAILED = "auth_failed"
    SYSTEM = "system"


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), nullable=False, index=True)
    event: Mapped[LogEvent] = mapped_column(Enum(LogEvent), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Contexto (sem dados sensíveis)
    message_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<Log id={self.id} level={self.level} event={self.event}>"
