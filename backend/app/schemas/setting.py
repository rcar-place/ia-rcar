"""Schemas de configuração."""
from pydantic import BaseModel, Field


class SettingItem(BaseModel):
    key: str
    value: str
    description: str | None = None

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    ai_enabled: bool | None = None
    business_hour_start: int | None = Field(default=None, ge=0, le=23)
    business_hour_end: int | None = Field(default=None, ge=0, le=23)
    manual_approval_required: bool | None = None
    ai_confidence_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    blacklist_words: str | None = None
    max_response_length: int | None = Field(default=None, ge=50, le=2000)


class SettingsResponse(BaseModel):
    ai_enabled: bool
    business_hour_start: int
    business_hour_end: int
    manual_approval_required: bool
    ai_confidence_threshold: float
    blacklist_words: str
    max_response_length: int
