"""
Rotas de Autenticação.
Login, refresh de token e criação de usuário admin.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user, require_admin
from app.core.security.jwt import create_token_pair, decode_token
from app.core.security.password import verify_password, hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, TokenResponse, RefreshRequest, UserCreate, UserResponse
from app.core.logger.logger import get_logger

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger(__name__)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Autentica um usuário e retorna par de tokens JWT."""
    repo = UserRepository(db)
    user = await repo.get_by_username(body.username)

    if not user or not verify_password(body.password, user.hashed_password):
        logger.warning("Tentativa de login falhou para: %s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )

    token_pair = create_token_pair(user.id, user.username, user.is_admin)
    logger.info("Login bem-sucedido para usuário id=%d", user.id)

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Renova o access token usando um refresh token válido."""
    try:
        token_data = decode_token(body.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    repo = UserRepository(db)
    user = await repo.get_by_id(token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inativo")

    token_pair = create_token_pair(user.id, user.username, user.is_admin)
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
) -> UserResponse:
    """Cria um novo usuário administrador (requer admin)."""
    repo = UserRepository(db)
    if await repo.get_by_username(body.username) or await repo.get_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username ou email já em uso",
        )

    user = await repo.create(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        is_admin=body.is_admin,
    )
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Retorna dados do usuário autenticado."""
    repo = UserRepository(db)
    user = await repo.get_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UserResponse.model_validate(user)
