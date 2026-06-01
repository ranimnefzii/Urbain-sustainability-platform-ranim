"""Debug current failing endpoints - v2."""
import httpx, asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        r = await client.post("/api/v1/auth/login", json={
            "email": "seifabdaoui5@gmail.com", "password": "test1234", "role": "ADMIN"
        })
        print(f"LOGIN: {r.status_code}")
        print(f"  {r.text[:300]}")
        data = r.json()
        token = data.get("access_token") or data.get("data", {}).get("access_token") or data.get("token")
        if not token:
            print("NO TOKEN FOUND")
            return
        headers = {"Authorization": f"Bearer {token}"}

        paths = [
            "/api/v1/notifications/stats",
            "/api/v1/reports/stats",
            "/api/v1/reports/?page=1&size=20",
            "/api/v1/ai/insights?days=30",
            "/api/v1/ai/model-info",
        ]
        for path in paths:
            r = await client.get(path, headers=headers)
            print(f"\n{path} -> {r.status_code}")
            if r.status_code >= 400:
                print(f"  {r.text[:600]}")

asyncio.run(main())
