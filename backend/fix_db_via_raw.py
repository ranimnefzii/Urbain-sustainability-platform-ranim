import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async with engine.connect() as conn:
        # Need to cast to VARCHAR first since role uses a custom type
        r1 = await conn.execute(text("UPDATE users SET role = CAST(LOWER(CAST(role AS VARCHAR)) AS userrole) WHERE CAST(role AS VARCHAR) != LOWER(CAST(role AS VARCHAR))"))
        print(f"Fixed {r1.rowcount} role values")
        
        r2 = await conn.execute(text("UPDATE users SET status = CAST(LOWER(CAST(status AS VARCHAR)) AS userstatus) WHERE CAST(status AS VARCHAR) != LOWER(CAST(status AS VARCHAR))"))
        print(f"Fixed {r2.rowcount} status values")
        
        await conn.commit()
        
        result = await conn.execute(text("SELECT email, role, status FROM users"))
        for row in result:
            print(f"  {row.email}: role={row.role}, status={row.status}")
    
    await engine.dispose()

asyncio.run(fix())
