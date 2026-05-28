"""
Repositório de Configurações do sistema.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.setting import Setting, DEFAULT_SETTINGS, SettingKeys


class SettingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> str | None:
        result = await self._session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    async def get_all(self) -> dict[str, str]:
        result = await self._session.execute(select(Setting))
        settings = result.scalars().all()
        return {s.key: s.value for s in settings}

    async def set(self, key: str, value: str) -> Setting:
        result = await self._session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            self._session.add(setting)
        await self._session.flush()
        return setting

    async def get_int(self, key: str, default: int = 0) -> int:
        value = await self.get(key)
        try:
            return int(value) if value is not None else default
        except ValueError:
            return default

    async def get_bool(self, key: str, default: bool = False) -> bool:
        value = await self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes")

    async def get_float(self, key: str, default: float = 0.0) -> float:
        value = await self.get(key)
        try:
            return float(value) if value is not None else default
        except ValueError:
            return default

    async def initialize_defaults(self) -> None:
        """Garante que as configurações padrão existam no banco."""
        for key, (value, description) in DEFAULT_SETTINGS.items():
            result = await self._session.execute(
                select(Setting).where(Setting.key == key)
            )
            if not result.scalar_one_or_none():
                self._session.add(Setting(key=key, value=value, description=description))
        await self._session.flush()
