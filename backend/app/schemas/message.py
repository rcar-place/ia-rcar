"""Schemas Pydantic para Mensagens e Respostas."""
from datetime import datetime
from pydantic import BaseModel
from app.models.message import MessageStatus
from app.models.response import ResponseStatus


class ResponseOut(BaseModel):
    id: int
    text: str
    model_used: str
    tokens_used: int
    confidence_score: float
    was_filtered: bool
    status: ResponseStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: int
    ml_message_id: str
    ml_conversation_id: str
    ml_buyer_id: str
    ml_buyer_nickname: str | None
    ml_item_id: str | None
    text_sanitized: str
    status: MessageStatus
    is_outside_business_hours: bool
    ai_confidence_score: float | None
    requires_manual_review: bool
    created_at: datetime
    response: ResponseOut | None = None

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    items: list[MessageOut]
    total: int
    page: int
    per_page: int


class ApproveRequest(BaseModel):
    approved: bool
    reason: str | None = None


class DashboardStats(BaseModel):
    total_messages: int
    responded: int
    pending: int
    ignored: int
    errors: int
    ai_enabled: bool
    is_business_hours: bool
    ws_connections: int
