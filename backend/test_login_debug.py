import asyncio, traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.security import verify_password
from app.models.user import User, UserRole, UserStatus

async def test():
    engine = create_async_engine('postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            result = await session.execute(text("SELECT * FROM users WHERE email = 'admin@urbain.com'"))
            row = result.fetchone()
            if row:
                print(f"role from DB: {row.role!r}")
                print(f"UserRole.ADMIN: {UserRole.ADMIN!r}")
                
                # Simulate what the login method does
                from app.core.security import create_access_token, create_refresh_token
                from datetime import timedelta
                
                role_val = row.role
                print(f"role_val: {role_val!r}")
                print(f"type: {type(role_val)}")
                
                try:
                    role_enum = UserRole(role_val)
                    print(f"role_enum: {role_enum!r}")
                except Exception as e:
                    print(f"Error creating enum: {e}")
                
                try:
                    token = create_access_token(
                        data={"sub": str(row.id), "role": row.role},
                    )
                    print(f"Token created: {token[:30]}...")
                except Exception as e:
                    print(f"Error creating token: {e}")
                    traceback.print_exc()
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
    
    await engine.dispose()

asyncio.run(test())
