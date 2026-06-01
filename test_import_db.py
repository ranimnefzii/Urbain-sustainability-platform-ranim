import subprocess, sys

# Test: try importing app.core.database specifically
print("Test: import app.core.database")
result = subprocess.run(
    [sys.executable, "-c", "import app.core.database; print('OK')"],
    capture_output=True, text=True, timeout=20,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
