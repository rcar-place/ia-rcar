"""
Schemas Pydantic para Webhooks do Mercado Livre.
Valida estritamente os dados recebidos antes de qualquer processamento.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class MLWebhookPayload(BaseModel):
    """Schema para notificações de webhook do Mercado Livre."""

    resource: str = Field(..., min_length=1, max_length=500)
    user_id: int = Field(..., gt=0)
    topic: str = Field(..., min_length=1, max_length=100)
    application_id: int
    attempts: int = Field(default=1, ge=1)
    sent: str = Field(..., min_length=1)
    received: str = Field(..., min_length=1)

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        allowed = {"messages", "orders_v2", "payments", "questions", "items"}
        if v not in allowed:
            raise ValueError(f"Tópico não suportado: {v}")
        return v


class MLMessageData(BaseModel):
    """Dados extraídos de uma mensagem do ML."""

    message_id: str
    conversation_id: str
    buyer_id: str
    buyer_nickname: str | None = None
    item_id: str | None = None
    text: str = Field(..., min_length=1, max_length=2000)
