"""
Rotas de Configurações do sistema.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import require_admin, get_current_user
from app.models.setting import SettingKeys
from app.repositories.setting_repository import SettingRepository
from app.schemas.setting import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> SettingsResponse:
    """Retorna todas as configurações atuais."""
    repo = SettingRepository(db)
    return SettingsResponse(
        ai_enabled=await repo.get_bool(SettingKeys.AI_ENABLED, True),
        business_hour_start=await repo.get_int(SettingKeys.BUSINESS_HOUR_START, 8),
        business_hour_end=await repo.get_int(SettingKeys.BUSINESS_HOUR_END, 18),
        manual_approval_required=await repo.get_bool(SettingKeys.MANUAL_APPROVAL_REQUIRED, False),
        ai_confidence_threshold=await repo.get_float(SettingKeys.AI_CONFIDENCE_THRESHOLD, 0.7),
        blacklist_words=await repo.get(SettingKeys.BLACKLIST_WORDS) or "",
        max_response_length=await repo.get_int(SettingKeys.MAX_RESPONSE_LENGTH, 500),
    )


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
) -> SettingsResponse:
    """Atualiza configurações do sistema (requer admin)."""
    repo = SettingRepository(db)

    updates = {
        SettingKeys.AI_ENABLED: body.ai_enabled,
        SettingKeys.BUSINESS_HOUR_START: body.business_hour_start,
        SettingKeys.BUSINESS_HOUR_END: body.business_hour_end,
        SettingKeys.MANUAL_APPROVAL_REQUIRED: body.manual_approval_required,
        SettingKeys.AI_CONFIDENCE_THRESHOLD: body.ai_confidence_threshold,
        SettingKeys.BLACKLIST_WORDS: body.blacklist_words,
        SettingKeys.MAX_RESPONSE_LENGTH: body.max_response_length,
    }

    for key, value in updates.items():
        if value is not None:
            await repo.set(key, str(value).lower() if isinstance(value, bool) else str(value))

    return await get_settings(db=db, _user=None)
