import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async with engine.connect() as conn:
        cols = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'priorities'"))
        print("Columns:", [c[0] for c in cols])
        result = await conn.execute(text("SELECT id, name FROM priorities"))
        for row in result:
            print(f"  id={row.id}, name={row.name}")
    await engine.dispose()

asyncio.run(check())
