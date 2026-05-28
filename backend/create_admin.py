import asyncio
import sys
import os

# Ajustar path se necessário
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database.engine import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security.password import hash_password

async def create_admin():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        try:
            user = await repo.get_by_username("admin")
            if not user:
                user = await repo.create(
                    username="admin",
                    email="admin@mlautoresponder.com",
                    hashed_password=hash_password("admin123"),
                    is_admin=True
                )
                await session.commit()
                print("SUCCESS: Usuário 'admin' criado com senha 'admin123'")
            else:
                user.hashed_password = hash_password("admin123")
                await session.commit()
                print("SUCCESS: Senha do usuário 'admin' resetada para 'admin123'")
        except Exception as e:
            print(f"ERROR: Falha ao criar usuário: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin())
