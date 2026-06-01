"""Directly test auth_service.login to see the error."""
import asyncio, traceback, sys
sys.path.insert(0, '.')
from app.core.database import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin
from app.core.exceptions import AuthenticationError

async def debug():
    async with AsyncSessionLocal() as session:
        svc = AuthService(session)
        login_data = UserLogin(email="admin@urbain.com", password="Admin123!")
        try:
            result = await svc.login(login_data)
            print(f"SUCCESS: {result['access_token'][:30]}...")
        except AuthenticationError as e:
            print(f"AuthError: {e.message}")
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()

asyncio.run(debug())
