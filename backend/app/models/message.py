"""Model de Mensagem recebida do Mercado Livre."""
import enum
from sqlalchemy import Enum, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.base import Base


class MessageStatus(str, enum.Enum):
    RECEIVED = "received"        # Recebida, aguardando processamento
    PROCESSING = "processing"    # Em processamento pela IA
    RESPONDED = "responded"      # Resposta enviada
    PENDING_APPROVAL = "pending_approval"  # Aguarda aprovação manual
    APPROVED = "approved"        # Aprovada manualmente
    REJECTED = "rejected"        # Rejeitada manualmente
    ERROR = "error"              # Erro no processamento
    IGNORED = "ignored"          # Ignorada (horário comercial)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # IDs do Mercado Livre
    ml_message_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    ml_conversation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ml_buyer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ml_buyer_nickname: Mapped[str] = mapped_column(String(255), nullable=True)
    ml_item_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Conteúdo
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sanitized: Mapped[str] = mapped_column(Text, nullable=False)

    # Status e controle
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus),
        default=MessageStatus.RECEIVED,
        nullable=False,
        index=True,
    )
    is_outside_business_hours: Mapped[bool] = mapped_column(default=False)
    ai_confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_manual_review: Mapped[bool] = mapped_column(default=False)

    # Relacionamento
    response: Mapped["Response"] = relationship("Response", back_populates="message", uselist=False)

    def __repr__(self) -> str:
        return f"<Message id={self.id} ml_id={self.ml_message_id} status={self.status}>"
