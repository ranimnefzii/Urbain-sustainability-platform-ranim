"""Debug login failure by simulating what AuthService.login does."""
import asyncio, traceback, sys
sys.path.insert(0, '.')
from app.core.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.user import UserLogin
from app.models.user import UserRole, UserStatus

async def debug():
    async with AsyncSessionLocal() as session:
        try:
            repo = UserRepository(db=session, model=User)
            user = await repo.get_by_email('admin@urbain.com')
            if not user:
                print("USER NOT FOUND")
                return
            
            print(f"user object: {user}")
            print(f"user.role: {user.role!r} (type={type(user.role).__name__})")
            print(f"user.status: {user.status!r} (type={type(user.status).__name__})")
            
            # Try accessing .value
            try:
                rv = user.role.value
                print(f"user.role.value = {rv!r}")
            except Exception as e:
                print(f"ERROR accessing role.value: {e}")
            
            try:
                sv = user.status.value
                print(f"user.status.value = {sv!r}")
            except Exception as e:
                print(f"ERROR accessing status.value: {e}")
            
            # Check password
            pw_ok = verify_password('Admin123!', user.hashed_password)
            print(f"Password verify: {pw_ok}")
            
            # Check status
            print(f"user.status == UserStatus.ACTIVE: {user.status == UserStatus.ACTIVE}")
            print(f"user.status == UserStatus.SUSPENDED: {user.status == UserStatus.SUSPENDED}")
            print(f"user.status == UserStatus.INACTIVE: {user.status == UserStatus.INACTIVE}")
            print(f"user.status == UserStatus.PENDING_VERIFICATION: {user.status == UserStatus.PENDING_VERIFICATION}")
            
            # Try to create token
            try:
                token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
                print(f"Token created: {token[:30]}...")
            except Exception as e:
                print(f"ERROR creating token: {e}")
                traceback.print_exc()
                
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()

asyncio.run(debug())
