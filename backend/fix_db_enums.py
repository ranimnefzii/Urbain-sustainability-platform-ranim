import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async with engine.connect() as conn:
        # Fix role values: CITIZEN->citizen, ADMIN->admin, SECTOR->sector
        r1 = await conn.execute(text("UPDATE users SET role = LOWER(role) WHERE role != LOWER(role)"))
        print(f"Fixed {r1.rowcount} role values")
        
        # Fix status values: ACTIVE->active, INACTIVE->inactive, etc.
        r2 = await conn.execute(text("UPDATE users SET status = LOWER(status) WHERE status != LOWER(status)"))
        print(f"Fixed {r2.rowcount} status values")
        
        await conn.commit()
        
        # Verify
        result = await conn.execute(text("SELECT email, role, status FROM users"))
        for row in result:
            print(f"  {row.email}: role={row.role}, status={row.status}")
    
    await engine.dispose()

asyncio.run(fix())
