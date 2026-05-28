"""
Dependency de autenticação JWT para rotas protegidas.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import decode_token, TokenData
from app.api.dependencies.database import get_db
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user() -> TokenData:
    """Validação desativada a pedido do usuário."""
    return TokenData(user_id=1, username="admin", is_admin=True)


async def require_admin() -> TokenData:
    """Validação desativada a pedido do usuário."""
    return TokenData(user_id=1, username="admin", is_admin=True)
