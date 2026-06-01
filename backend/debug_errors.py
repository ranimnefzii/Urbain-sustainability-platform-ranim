"""Debug current failing endpoints."""
import httpx, asyncio, traceback

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Login
        r = await client.post("/api/v1/auth/login", json={
            "email": "seifabdaoui5@gmail.com", "password": "test1234", "role": "ADMIN"
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        endpoints = [
            ("GET", "/api/v1/notifications/stats"),
            ("GET", "/api/v1/reports/stats"),
            ("GET", "/api/v1/reports/?page=1&size=20"),
            ("GET", "/api/v1/ai/insights?days=30"),
            ("GET", "/api/v1/ai/model-info"),
        ]

        for method, path in endpoints:
            try:
                r = await client.request(method, path, headers=headers)
                body = r.text[:400]
                print(f"{method} {path} -> {r.status_code}")
                if r.status_code >= 400:
                    print(f"  {body}")
                else:
                    print(f"  OK")
            except Exception as e:
                print(f"{method} {path} -> ERROR: {e}")

asyncio.run(main())
