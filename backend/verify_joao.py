import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database.engine import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security.password import verify_password
from sqlalchemy import select
from app.models.user import User

async def main():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_by_username("joao")
        if not user:
            print("User joao not found by get_by_username!")
            result = await session.execute(select(User).where(User.username == "joao"))
            u2 = result.scalar_one_or_none()
            if u2:
                print("User joao exists but is_active =", u2.is_active)
            else:
                print("User joao completely missing!")
        else:
            print("User joao found, is_active:", user.is_active)
            print("Password verification (2468):", verify_password("2468", user.hashed_password))

if __name__ == "__main__":
    asyncio.run(main())
