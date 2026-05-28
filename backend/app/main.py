"""
Ponto de entrada principal do FastAPI.
Configura middlewares, rotas, CORS, rate limiting e startup.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config.settings import settings
from app.core.database.engine import engine
from app.core.database.base import Base
from app.core.logger.logger import get_logger
from app.api.middlewares.error_handler import ErrorHandlerMiddleware
from app.api.middlewares.logging_middleware import LoggingMiddleware
from app.api.routes import auth, messages, settings as settings_router, logs, webhook, websocket

logger = get_logger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown do aplicativo."""
    logger.info("🚀 Iniciando %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Cria tabelas se não existirem (use Alembic em produção)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Inicializa configurações padrão e cria usuário inicial se não existir
    from app.core.database.engine import AsyncSessionLocal
    from app.repositories.setting_repository import SettingRepository
    from app.repositories.user_repository import UserRepository
    from app.core.security.password import hash_password
    
    async with AsyncSessionLocal() as session:
        # Cria/Atualiza configurações
        repo_settings = SettingRepository(session)
        await repo_settings.initialize_defaults()
        
        # Cria usuário joao automaticamente na nuvem se não existir
        repo_user = UserRepository(session)
        user = await repo_user.get_by_username("joao")
        if not user:
            await repo_user.create(
                username="joao",
                email="joao@mlautoresponder.com",
                hashed_password=hash_password("2468"),
                is_admin=True
            )
            logger.info("Usuário 'joao' criado automaticamente!")
            
        await session.commit()

    logger.info("✅ Banco de dados inicializado")
    yield

    logger.info("🛑 Encerrando aplicação")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Rate Limiting ──────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Middlewares (ordem importa) ─────────────────────────────────────────
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Signature"],
        expose_headers=["X-Total-Count"],
    )

    # ── Rotas ──────────────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(webhook.router, prefix=prefix)
    app.include_router(auth.router, prefix=prefix)
    app.include_router(messages.router, prefix=prefix)
    app.include_router(settings_router.router, prefix=prefix)
    app.include_router(logs.router, prefix=prefix)
    app.include_router(websocket.router)  # WebSocket sem prefixo /api/v1

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()
