Dim WshShell, AppPath, BackendDir
Set WshShell = CreateObject("WScript.Shell")
BackendDir = "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
AppPath = "C:\Users\seifa\AppData\Local\Programs\Python\Python313\pythonw.exe"
WshShell.CurrentDirectory = BackendDir

' Explicitly set all env vars that .env would provide
Dim env: Set env = WshShell.Environment("PROCESS")
env("DATABASE_URL") = "postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability"
env("SECRET_KEY") = "urbain-super-secret-key-change-in-production-2024"
env("ALLOWED_ORIGINS") = "[""http://localhost:3000"",""http://localhost:5173"",""http://localhost:5174""]"
env("DEBUG") = "True"
env("SMTP_HOST") = "smtp.gmail.com"
env("SMTP_PORT") = "587"
env("SMTP_USERNAME") = "seifabdaoui5@gmail.com"
env("SMTP_PASSWORD") = "jour apgx exhb mzge"
env("EMAIL_FROM") = "seifabdaoui5@gmail.com"
env("EMAIL_FROM_NAME") = "Urbain Sustainability System"

WshShell.Run AppPath & " -m uvicorn app.main:app --host 127.0.0.1 --port 8001", 0, False
Set WshShell = Nothing
