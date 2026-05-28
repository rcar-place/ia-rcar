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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> TokenData:
    """Valida o token JWT e retorna os dados do usuário."""
    try:
        token_data = decode_token(credentials.credentials, expected_type="access")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se usuário ainda existe e está ativo
    repo = UserRepository(db)
    user = await repo.get_by_id(token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou não encontrado",
        )

    return token_data


async def require_admin(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Exige que o usuário seja administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user
