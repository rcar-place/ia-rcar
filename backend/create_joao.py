import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database.engine import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security.password import hash_password

async def create_user():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        try:
            user = await repo.get_by_username("joao")
            if not user:
                user = await repo.create(
                    username="joao",
                    email="joao@mlautoresponder.com",
                    hashed_password=hash_password("2468"),
                    is_admin=True
                )
                await session.commit()
                print("SUCCESS: Usuário 'joao' criado com senha '2468'")
            else:
                user.hashed_password = hash_password("2468")
                await session.commit()
                print("SUCCESS: Senha do usuário 'joao' resetada para '2468'")
        except Exception as e:
            print(f"ERROR: Falha ao criar usuário: {e}")

if __name__ == "__main__":
    asyncio.run(create_user())
