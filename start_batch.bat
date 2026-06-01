@echo off
cd /d "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
set DATABASE_URL=postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability
set SECRET_KEY=urbain-super-secret-key-change-in-production-2024
set DEBUG=True
set ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:5174"]
start /b pythonw -m uvicorn app.main:app --host 127.0.0.1 --port 8001
echo Server started from batch
