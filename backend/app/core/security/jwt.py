"""
Utilitários de segurança JWT.
Criação e validação de access tokens e refresh tokens.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config.settings import settings
from app.core.logger.logger import get_logger

logger = get_logger(__name__)


class TokenData(BaseModel):
    user_id: int
    username: str
    is_admin: bool = False


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def create_access_token(data: dict[str, Any]) -> str:
    """Cria um access token JWT com expiração curta."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Cria um refresh token JWT com expiração longa."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_token_pair(user_id: int, username: str, is_admin: bool) -> TokenPair:
    """Cria par access + refresh token."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
    }
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )


def decode_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Decodifica e valida um JWT.
    Lança ValueError em caso de token inválido ou expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != expected_type:
            raise ValueError("Tipo de token inválido")

        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id or not username:
            raise ValueError("Token malformado")

        return TokenData(
            user_id=int(user_id),
            username=username,
            is_admin=payload.get("is_admin", False),
        )
    except JWTError as e:
        logger.warning("Token JWT inválido: %s", str(e))
        raise ValueError("Token inválido ou expirado") from e
