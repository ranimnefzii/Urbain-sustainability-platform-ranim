import asyncio, traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.repositories.user_repository import UserRepository

async def test():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            repo = UserRepository(session)
            user = await repo.get_by_email('admin@urbain.com')
            if user:
                print(f"user.role: {user.role!r}")
                print(f"type: {type(user.role)}")
                print(f"user.status: {user.status!r}")
                print(f"type: {type(user.status)}")
                try:
                    print(f"user.role.value: {user.role.value}")
                except Exception as e:
                    print(f"Error accessing .value: {e}")
            else:
                print("User not found")
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
    
    await engine.dispose()

asyncio.run(test())
