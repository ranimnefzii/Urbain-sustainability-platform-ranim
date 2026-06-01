import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT email, hashed_password FROM users WHERE email = 'admin@urbain.com'"))
            for row in result:
                print(f'Email: {row[0]}')
                print(f'Hash: {row[1][:80]}...')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        await engine.dispose()

asyncio.run(check())
