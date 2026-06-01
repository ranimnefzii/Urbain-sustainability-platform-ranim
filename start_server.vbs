Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
WshShell.Environment("PROCESS")("PYTHONPATH") = "C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend"
WshShell.Run "python -m uvicorn app.main:app --host 127.0.0.1 --port 8001", 0, False
