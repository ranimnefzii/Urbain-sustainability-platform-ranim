import asyncio, asyncpg, bcrypt

async def test():
    conn = await asyncpg.connect('postgresql://username:password@localhost:5433/urbain_sustainability')
    row = await conn.fetchrow('SELECT id, email, hashed_password FROM users WHERE email = $1', 'admin@urbain.com')
    print(f"ID={row['id']} Email={row['email']}")
    print(f"Hash: {row['hashed_password'][:50]}...")
    
    pw = b'Admin123!'
    result = bcrypt.checkpw(pw, row['hashed_password'].encode())
    print(f"Password match: {result}")
    
    await conn.close()

asyncio.run(test())
