Dim WshShell, AppPath, BackendDir
Set WshShell = CreateObject("WScript.Shell")
BackendDir = "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
AppPath = "C:\Users\seifa\AppData\Local\Programs\Python\Python313\python.exe"
WshShell.CurrentDirectory = BackendDir
WshShell.Run AppPath & " -m uvicorn app.main:app --host 127.0.0.1 --port 8001", 0, False
Set WshShell = Nothing
