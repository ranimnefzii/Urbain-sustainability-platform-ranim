import sys
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')

# Test 1: Can we import Settings and get the right DB URL?
from app.core.config import settings
print(f"1. DB URL: {settings.DATABASE_URL}")
print(f"2. Port: {settings.DATABASE_URL.split('@')[1].split('/')[0].split(':')[1] if ':' in settings.DATABASE_URL.split('@')[1].split('/')[0] else 'default' }")

# Test 2: Test direct connection to DB  
import asyncio
import asyncpg

async def test_db():
    try:
        conn = await asyncpg.connect(
            'postgresql://username:password@localhost:5433/urbain_sustainability',
            timeout=5
        )
        row = await conn.fetchrow('SELECT id, email FROM users WHERE email = $1', 'admin@urbain.com')
        print(f"3. DB user: id={row['id'] if row else None}, email={row['email'] if row else None}")
        await conn.close()
    except Exception as e:
        print(f"3. DB error: {type(e).__name__}: {e}")

asyncio.run(test_db())
