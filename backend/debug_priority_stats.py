"""Debug priority stats endpoint."""
import asyncio, traceback, sys
sys.path.insert(0, '.')
from app.core.database import AsyncSessionLocal
from app.services.priority_service import PriorityService

async def debug():
    async with AsyncSessionLocal() as session:
        svc = PriorityService(session)
        try:
            result = await svc.get_priority_stats(priority_id=1)
            print(f"SUCCESS: {result}")
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()

asyncio.run(debug())
