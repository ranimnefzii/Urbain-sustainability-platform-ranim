import sys
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')

import asyncio
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin

async def test_login_direct():
    async for session in get_db():
        service = AuthService(session)
        try:
            result = await service.login(UserLogin(
                email="admin@urbain.com",
                password="Admin123!",
                remember_me=False
            ))
            print(f"SUCCESS! Token: {result['access_token'][:20]}...")
        except Exception as e:
            print(f"FAILED: {type(e).__name__}: {e}")
        break

asyncio.run(test_login_direct())
