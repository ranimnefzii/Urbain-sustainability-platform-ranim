import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.security import verify_password

async def test():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM users WHERE email = 'admin@urbain.com'"))
        row = result.fetchone()
        if row:
            columns = result.keys()
            for i, col in enumerate(columns):
                val = row[i]
                print(f"  {col}: {str(val)[:80]}")
            
            print(f"\nPassword verify: {verify_password('Admin123!', row.hashed_password)}")
    
    await engine.dispose()

asyncio.run(test())
