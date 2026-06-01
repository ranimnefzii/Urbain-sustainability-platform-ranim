import sys
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

async def test_sa():
    print(f"1. URL: {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    try:
        async with engine.connect() as conn:
            print("2. Connected!")
            result = await conn.execute(text("SELECT id, email FROM users WHERE email = 'admin@urbain.com'"))
            row = result.first()
            print(f"3. User: {row}")
    except Exception as e:
        print(f"2. Error: {type(e).__name__}: {e}")
    finally:
        await engine.dispose()

asyncio.run(test_sa())
