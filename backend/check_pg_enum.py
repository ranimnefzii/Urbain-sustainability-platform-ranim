import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT t.typname, e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            ORDER BY t.typname, e.enumsortorder
        """))
        print("PostgreSQL enums:")
        for row in result:
            print(f"  {row.typname}: {row.enumlabel}")
    
    await engine.dispose()

asyncio.run(check())
