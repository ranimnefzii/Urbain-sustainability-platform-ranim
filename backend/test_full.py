"""Test all endpoints that were previously failing."""
import requests, json

BASE = "http://localhost:8000/api/v1"

# Step 1: Login
r = requests.post(f"{BASE}/auth/login", json={
    "email": "admin@urbain.com",
    "password": "Admin123!"
})
print(f"1. LOGIN: {r.status_code}")
if r.status_code == 200:
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Token: {token[:40]}...")
else:
    print(f"   ERROR: {r.text}")
    exit(1)

# Step 2: Test GET /signals/
r = requests.get(f"{BASE}/signals/?page=1&size=20", headers=headers)
print(f"\n2. GET /signals/: {r.status_code}")
print(f"   Response: {r.text[:200]}")

# Step 3: Test GET /admin/stats/signals
r = requests.get(f"{BASE}/admin/stats/signals", headers=headers)
print(f"\n3. GET /admin/stats/signals: {r.status_code}")
print(f"   Response: {r.text[:200]}")

# Step 4: Test GET /priorities/1/stats
r = requests.get(f"{BASE}/priorities/1/stats", headers=headers)
print(f"\n4. GET /priorities/1/stats: {r.status_code}")
if r.status_code != 200:
    print(f"   Response: {r.text[:300]}")
else:
    print(f"   Response: {r.text[:200]}")

# Step 5: Test GET /priorities/2/stats
r = requests.get(f"{BASE}/priorities/2/stats", headers=headers)
print(f"\n5. GET /priorities/2/stats: {r.status_code}")
if r.status_code != 200:
    print(f"   Response: {r.text[:300]}")
else:
    print(f"   Response: {r.text[:200]}")
