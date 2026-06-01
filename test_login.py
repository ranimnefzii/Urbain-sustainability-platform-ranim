import sys
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')
import asyncio
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.core.database import get_session

async def test():
    print(f"DB URL: {settings.DATABASE_URL}")
    print(f"Secret key: {settings.SECRET_KEY[:10]}...")
    
    async for session in get_session():
        try:
            repo = UserRepository(session)
            user = await repo.get_by_email("admin@urbain.com")
            if user:
                print(f"User found: id={user.id}, email={user.email}, status={user.status}")
            else:
                print("User NOT found!")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
        break

asyncio.run(test())
