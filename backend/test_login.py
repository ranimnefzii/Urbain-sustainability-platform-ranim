import requests, json

url = "http://localhost:8000/api/v1/auth/login"
payload = {"email": "admin@urbain.com", "password": "Admin123!"}
r = requests.post(url, json=payload)
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Body: {r.text}")
