import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole, UserStatus

async def test():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == 'admin@urbain.com'))
        user = result.scalar_one_or_none()
        if user:
            print(f"user.role: {user.role!r}")
            print(f"type: {type(user.role)}")
            print(f"user.status: {user.status!r}")
            print(f"type: {type(user.status)}")
            
            try:
                print(f"user.role.value: {user.role.value}")
            except Exception as e:
                print(f"Error accessing .value: {e}")
            
            try:
                is_admin = user.role == UserRole.ADMIN
                print(f"user.role == UserRole.ADMIN: {is_admin}")
            except Exception as e:
                print(f"Error comparing: {e}")
        else:
            print("User not found")
    
    await engine.dispose()

asyncio.run(test())
