import subprocess, sys

# Test importing app.core.config directly
print("Test: import app.core.config")
result = subprocess.run(
    [sys.executable, "-c", "import app.core.config; print('OK')"],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

if result.returncode != 0:
    print("\nFirst attempt failed! Let me test with timeout 60s...")
    result2 = subprocess.run(
        [sys.executable, "-c", "import app.core.config; print('OK')"],
        capture_output=True, text=True, timeout=60,
        cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
    )
    print("STDOUT:", result2.stdout)
    print("STDERR:", result2.stderr)
    print("RC:", result2.returncode)
