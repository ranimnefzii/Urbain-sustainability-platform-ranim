import subprocess, sys, time

# Test: import app.core.config with longer timeout
print(f"Start: {time.strftime('%H:%M:%S')}")
result = subprocess.run(
    [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); import app.core.config; s = app.core.config.settings; print('OK'); print('DB:', s.DATABASE_URL[:30])"],
    capture_output=True, text=True, timeout=60,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print(f"End: {time.strftime('%H:%M:%S')}")
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
