"""Debug the admin/stats/signals endpoint directly."""
import asyncio, traceback, sys
sys.path.insert(0, '.')
from app.core.database import AsyncSessionLocal
from app.services.signal_service import SignalService

async def debug():
    async with AsyncSessionLocal() as session:
        svc = SignalService(session)
        try:
            result = await svc.get_signal_stats()
            print(f"SUCCESS: {result}")
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()

asyncio.run(debug())
