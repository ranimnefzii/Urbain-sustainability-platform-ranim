import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT
                tc.constraint_name, tc.constraint_type,
                kcu.column_name, ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'categories'
        """))
        for row in result:
            print(f"  {row}")
    await engine.dispose()

asyncio.run(check())
