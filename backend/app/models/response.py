"""Model de Resposta gerada pela IA."""
import enum
from sqlalchemy import Enum, ForeignKey, Text, Float, Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.base import Base


class ResponseStatus(str, enum.Enum):
    GENERATED = "generated"    # Gerada pela IA
    SENT = "sent"              # Enviada ao ML
    FAILED = "failed"          # Falha ao enviar
    BLOCKED = "blocked"        # Bloqueada pelo filtro de segurança


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False, index=True)

    # Conteúdo
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadados da IA
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    was_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[ResponseStatus] = mapped_column(
        Enum(ResponseStatus),
        default=ResponseStatus.GENERATED,
        nullable=False,
    )
    ml_response_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relacionamento
    message: Mapped["Message"] = relationship("Message", back_populates="response")

    def __repr__(self) -> str:
        return f"<Response id={self.id} msg_id={self.message_id} status={self.status}>"
