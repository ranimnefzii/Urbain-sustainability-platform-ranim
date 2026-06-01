import subprocess, sys

# Test importing the actual config module from backend dir
result = subprocess.run(
    [sys.executable, "-c", "import app.core.config; print('IMPORT OK')"],
    capture_output=True, text=True, timeout=30,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("Import config module test:")
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

# Try with PYTHONPATH
result2 = subprocess.run(
    [sys.executable, "-c", "import app.core.config; s = app.core.config.settings; print(f'DB={s.DATABASE_URL}')"],
    capture_output=True, text=True, timeout=30,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend',
    env={**subprocess.os.environ, 'PYTHONPATH': r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'}
)
print("\nWith PYTHONPATH:")
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
print("RC:", result2.returncode)
