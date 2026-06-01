Dim WshShell, AppPath, BackendDir, EnvString
Set WshShell = CreateObject("WScript.Shell")
BackendDir = "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
AppPath = "C:\Users\seifa\AppData\Local\Programs\Python\Python313\pythonw.exe"
WshShell.CurrentDirectory = BackendDir
WshShell.Environment("PROCESS")("DATABASE_URL") = "postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability"
WshShell.Run AppPath & " -m uvicorn app.main:app --host 127.0.0.1 --port 8001", 0, False
Set WshShell = Nothing
