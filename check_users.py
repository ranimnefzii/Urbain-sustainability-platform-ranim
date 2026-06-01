import asyncio, asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://username:password@localhost:5433/urbain_sustainability')
    rows = await conn.fetch('SELECT id, email, role, status, first_name, last_name FROM users')
    for r in rows:
        print(f"ID={r['id']} Email={r['email']} Role={r['role']} Status={r['status']} Name={r['first_name']} {r['last_name']}")
    await conn.close()

asyncio.run(test())
